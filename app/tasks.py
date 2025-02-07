from celery import Celery
from PIL import Image
from io import BytesIO
import base64
import torch
import os

celery_app = Celery('tasks',
                    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
                    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/1'))

celery_app.conf.update(
    result_expires=3600,  # 60 minutes in seconds
    broker_transport_options={
        'visibility_timeout': 7200  # 2 hours for task visibility
    }
)

@celery_app.task(bind=True, acks_late=True)
def process_image_task(self, image_b64, categories):  # Remove task_id from args
    # Lazy load model (add error handling)
    if not hasattr(process_image_task, 'model'):
        try:
            from .models.loader import load_model
            process_image_task.model, process_image_task.processor = load_model()
            torch.set_num_threads(1)
        except Exception as e:
            self.retry(exc=e, countdown=30, max_retries=3)
    
    try:
        img = Image.open(BytesIO(base64.b64decode(image_b64)))
        result = get_feats_vqa(
            img, 
            categories, 
            process_image_task.model, 
            process_image_task.processor
        )
        return result
    except Exception as e:
        self.retry(exc=e, countdown=15, max_retries=3)

def get_feats_vqa(image, categories, model, processor):
    rated_categories = {}
    inputs = processor(images=image, text=categories, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    for i, cat in enumerate(categories):
        rated_categories[cat] = probs[0, i].item()
    return rated_categories