#!/bin/bash

celery -A celery_tasks.tasks worker -l info

$@