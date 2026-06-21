-- Add missing columns to videos table
alter table public.videos add column if not exists duration  text;
alter table public.videos add column if not exists thumbnail text;

-- Allow admins/editors to update and delete videos
create policy if not exists "Editors update videos" on public.videos for update using (
  exists (select 1 from public.profiles where id = auth.uid() and role in ('editor','admin'))
);
create policy if not exists "Editors delete videos" on public.videos for delete using (
  exists (select 1 from public.profiles where id = auth.uid() and role in ('editor','admin'))
);
