-- ============================================================
-- LexBase Full Schema Migration
-- ============================================================

-- 1. DOMAINS TABLE
create table if not exists public.domains (
  id          text primary key,          -- e.g. 'civil', 'penal'
  name_fr     text not null,
  name_ar     text not null,
  icon        text not null,             -- Lucide icon name
  law_count   integer default 0,
  sub_domains text[] default '{}',
  created_at  timestamptz default now()
);

-- 2. LAWS TABLE
create table if not exists public.laws (
  id          bigserial primary key,
  number      text not null,             -- e.g. 'Dahir n°1-04-22'
  type        text not null,             -- Loi, Dahir, Décret, etc.
  domain_id   text references public.domains(id) on delete set null,
  status      text not null default 'En vigueur',  -- En vigueur | Abrogé | Modifié
  date        date,
  title_fr    text not null,
  title_ar    text,
  excerpt_fr  text,
  excerpt_ar  text,
  content_fr  text,
  content_ar  text,
  language    text default 'Bilingue',   -- FR | AR | Bilingue
  tags        text[] default '{}',
  pdf_url     text,                      -- Supabase Storage URL
  views       integer default 0,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

-- 3. PROFILES TABLE (extends Supabase auth.users)
create table if not exists public.profiles (
  id          uuid primary key references auth.users(id) on delete cascade,
  name        text,
  email       text,
  profession  text,
  role        text not null default 'user',  -- user | editor | admin
  avatar_url  text,
  created_at  timestamptz default now()
);

-- 4. FAVORITES TABLE
create table if not exists public.favorites (
  id         bigserial primary key,
  user_id    uuid references public.profiles(id) on delete cascade,
  law_id     bigint references public.laws(id) on delete cascade,
  created_at timestamptz default now(),
  unique(user_id, law_id)
);

-- 5. VIDEOS TABLE
create table if not exists public.videos (
  id          bigserial primary key,
  title_fr    text not null,
  title_ar    text,
  youtube_id  text not null,
  domain_id   text references public.domains(id) on delete set null,
  level       text default 'Débutant',   -- Débutant | Intermédiaire | Expert
  author      text,
  views       integer default 0,
  date        date,
  created_at  timestamptz default now()
);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

alter table public.domains  enable row level security;
alter table public.laws     enable row level security;
alter table public.profiles enable row level security;
alter table public.favorites enable row level security;
alter table public.videos   enable row level security;

-- Public read access (anyone can read laws, domains, videos)
create policy "Public read domains"   on public.domains   for select using (true);
create policy "Public read laws"      on public.laws      for select using (true);
create policy "Public read videos"    on public.videos    for select using (true);

-- Profiles: users manage their own
create policy "Users read own profile"   on public.profiles for select using (auth.uid() = id);
create policy "Users update own profile" on public.profiles for update using (auth.uid() = id);

-- Favorites: users manage their own
create policy "Users read own favorites"   on public.favorites for select using (auth.uid() = user_id);
create policy "Users insert own favorites" on public.favorites for insert with check (auth.uid() = user_id);
create policy "Users delete own favorites" on public.favorites for delete using (auth.uid() = user_id);

-- Editors and admins can write laws/videos
create policy "Editors insert laws"  on public.laws  for insert with check (
  exists (select 1 from public.profiles where id = auth.uid() and role in ('editor','admin'))
);
create policy "Editors update laws"  on public.laws  for update using (
  exists (select 1 from public.profiles where id = auth.uid() and role in ('editor','admin'))
);
create policy "Editors insert videos" on public.videos for insert with check (
  exists (select 1 from public.profiles where id = auth.uid() and role in ('editor','admin'))
);

-- ============================================================
-- AUTO-CREATE PROFILE ON SIGNUP
-- ============================================================
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id, name, email, role)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    new.email,
    'user'
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============================================================
-- SEED: 9 LEGAL DOMAINS
-- ============================================================
insert into public.domains (id, name_fr, name_ar, icon, law_count, sub_domains) values
  ('civil',          'Droit Civil',           'القانون المدني',      'Scale',     342, '{"Contrats","Famille","Propriété","Successions"}'),
  ('penal',          'Droit Pénal',            'القانون الجنائي',     'Gavel',     218, '{"Crimes","Délits","Contraventions","Procédure pénale"}'),
  ('commercial',     'Droit Commercial',       'القانون التجاري',     'Briefcase', 287, '{"Sociétés","Contrats commerciaux","Faillite","Bourse"}'),
  ('administratif',  'Droit Administratif',    'القانون الإداري',     'Building2', 195, '{"Fonction publique","Marchés publics","Urbanisme","Contentieux"}'),
  ('travail',        'Droit du Travail',       'قانون الشغل',         'Users',     156, '{"Contrat de travail","Syndicats","Sécurité sociale","Licenciement"}'),
  ('fiscal',         'Droit Fiscal',           'القانون الجبائي',     'Receipt',   234, '{"IS","IR","TVA","Douanes"}'),
  ('international',  'Droit International',    'القانون الدولي',      'Globe',      89, '{"Traités","Conventions","Droit humanitaire","Commerce international"}'),
  ('numerique',      'Droit Numérique',        'القانون الرقمي',      'Monitor',    67, '{"Protection des données","Cybercriminalité","E-commerce","Télécoms"}'),
  ('constitutionnel','Droit Constitutionnel',  'القانون الدستوري',    'Landmark',   45, '{"Constitution","Droits fondamentaux","Institutions","Élections"}')
on conflict (id) do nothing;

-- ============================================================
-- INDEXES for performance
-- ============================================================
create index if not exists laws_domain_idx  on public.laws(domain_id);
create index if not exists laws_type_idx    on public.laws(type);
create index if not exists laws_status_idx  on public.laws(status);
create index if not exists laws_date_idx    on public.laws(date desc);
create index if not exists favorites_user_idx on public.favorites(user_id);

-- Full-text search index (French + Arabic)
alter table public.laws add column if not exists search_vector tsvector
  generated always as (
    to_tsvector('french', coalesce(title_fr,'') || ' ' || coalesce(excerpt_fr,'') || ' ' || coalesce(number,''))
  ) stored;

create index if not exists laws_search_idx on public.laws using gin(search_vector);
