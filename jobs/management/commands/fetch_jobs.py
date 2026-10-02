from django.core.management.base import BaseCommand
from jobs.models import JobPosting
from jobs.sources import fetch_jsearch, fetch_adzuna, fetch_internshala
from matching.embeddings import embed_text



class Command(BaseCommand):
    help = "Fetch job postings from JSearch and Adzuna, embed them, and store them."

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, default='python developer')
        parser.add_argument('--location', type=str, default='India')

    def handle(self, *args, **options):
        query = options['query']
        location = options['location']
        all_jobs = []

        try:
            all_jobs += fetch_jsearch(query, location)
            self.stdout.write(self.style.SUCCESS(f"JSearch: fetched jobs"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"JSearch failed: {e}"))

        try:
            all_jobs += fetch_adzuna(query, location)
            self.stdout.write(self.style.SUCCESS(f"Adzuna: fetched jobs"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Adzuna failed: {e}"))

        # inside handle(), alongside the other try/except blocks:
        try:
            all_jobs += fetch_internshala(query, location)
            self.stdout.write(self.style.SUCCESS(f"Internshala: fetched jobs"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Internshala failed: {e}"))

        created_count = 0
        for job_data in all_jobs:
            if not job_data['title'] or not job_data['description']:
                continue
            if JobPosting.objects.filter(source_url=job_data['source_url']).exists():
                continue

            embedding = embed_text(job_data['description'])
            JobPosting.objects.create(
                title=job_data['title'],
                company=job_data['company'],
                description=job_data['description'],
                location=job_data['location'],
                source=job_data['source'],
                source_url=job_data['source_url'],
                embedding=embedding,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new job postings"))