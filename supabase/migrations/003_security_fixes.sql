-- ============================================================
-- Security fixes — missing RLS policies
-- Run this in Supabase SQL Editor
-- ============================================================

-- 1. Allow admins to DELETE laws
drop policy if exists "Admins delete laws" on public.laws;
create policy "Admins delete laws"
  on public.laws for delete
  using (
    exists (select 1 from public.profiles where id = auth.uid() and role = 'admin')
  );

-- 2. Allow admins to DELETE videos
drop policy if exists "Admins delete videos" on public.videos;
create policy "Admins delete videos"
  on public.videos for delete
  using (
    exists (select 1 from public.profiles where id = auth.uid() and role = 'admin')
  );

-- 3. Allow admins to UPDATE any user profile (role changes)
drop policy if exists "Admins update any profile" on public.profiles;
create policy "Admins update any profile"
  on public.profiles for update
  using (
    exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin')
  );

-- 4. Allow admins to READ all profiles (needed for user management table)
drop policy if exists "Admins read all profiles" on public.profiles;
create policy "Admins read all profiles"
  on public.profiles for select
  using (
    auth.uid() = id
    or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin')
  );

-- 5. Editors can UPDATE and DELETE videos they manage
drop policy if exists "Editors update videos" on public.videos;
create policy "Editors update videos"
  on public.videos for update
  using (
    exists (select 1 from public.profiles where id = auth.uid() and role in ('editor','admin'))
  );

drop policy if exists "Editors delete videos" on public.videos;
create policy "Editors delete videos"
  on public.videos for delete
  using (
    exists (select 1 from public.profiles where id = auth.uid() and role in ('editor','admin'))
  );

-- 6. Prevent privilege escalation: users cannot set their own role to admin/editor
drop policy if exists "Users update own profile non-role fields" on public.profiles;
create policy "Users update own profile non-role fields"
  on public.profiles for update
  using (auth.uid() = id)
  with check (
    (role = (select role from public.profiles where id = auth.uid()))
    or exists (select 1 from public.profiles p where p.id = auth.uid() and p.role = 'admin')
  );
