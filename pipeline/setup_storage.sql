-- Run this in Supabase SQL Editor ONCE to create the PDF storage bucket

-- Create storage bucket for legal documents
insert into storage.buckets (id, name, public)
values ('legal-documents', 'legal-documents', true)
on conflict (id) do nothing;

-- Allow public to read/download PDFs
create policy "Public read PDFs"
on storage.objects for select
using (bucket_id = 'legal-documents');

-- Allow editors/admins to upload PDFs via dashboard
create policy "Editors upload PDFs"
on storage.objects for insert
with check (
  bucket_id = 'legal-documents'
  and exists (
    select 1 from public.profiles
    where id = auth.uid()
    and role in ('editor', 'admin')
  )
);
