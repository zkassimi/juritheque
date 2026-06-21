-- ============================================================
-- Fix infinite recursion in RLS policies on profiles table
-- The previous policies queried profiles FROM WITHIN a profiles policy
-- → infinite recursion → fetchProfile silently fails → isAdmin = false
-- Solution: use a SECURITY DEFINER function that bypasses RLS
-- ============================================================

-- Step 1: Create a helper function that reads the current user's role
--         SECURITY DEFINER = runs as the function owner (bypasses RLS)
create or replace function public.get_my_role()
returns text
language sql
security definer
stable
set search_path = public
as $$
  select role from public.profiles where id = auth.uid()
$$;

-- Step 2: Drop the recursive policies
drop policy if exists "Admins read all profiles"            on public.profiles;
drop policy if exists "Admins update any profile"          on public.profiles;
drop policy if exists "Users update own profile non-role fields" on public.profiles;

-- Step 3: Recreate them using get_my_role() — no more recursion

-- Users can read their own profile, admins can read all
create policy "Admins read all profiles"
  on public.profiles for select
  using (
    auth.uid() = id
    or public.get_my_role() = 'admin'
  );

-- Admins can update any profile (e.g. change someone's role)
create policy "Admins update any profile"
  on public.profiles for update
  using (
    public.get_my_role() = 'admin'
  );

-- Regular users can update their own profile but cannot change their role
create policy "Users update own profile non-role fields"
  on public.profiles for update
  using (auth.uid() = id)
  with check (
    (role = public.get_my_role())
    or public.get_my_role() = 'admin'
  );
