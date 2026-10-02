from django.core.management.base import BaseCommand
from jobs.models import JobPosting
from matching.embeddings import embed_text
import time

class Command(BaseCommand):
    help = "Re-generate embeddings for all job postings using the current embedding provider."

    def handle(self, *args, **options):
        jobs = JobPosting.objects.all()
        total = jobs.count()
        success_count = 0
        fail_count = 0
        for i, job in enumerate(jobs, start=1):
            try:
                job.embedding = embed_text(job.description)
                job.save()
                success_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed on job {job.id}: {e}"))
                fail_count += 1
                time.sleep(2)
                continue
            if i % 20 == 0:
                self.stdout.write(f"Processed {i}/{total}")
        self.stdout.write(self.style.SUCCESS(f"Done: {success_count} succeeded, {fail_count} failed, out of {total}"))