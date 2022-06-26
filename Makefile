.PHONY: task-queue-init-db task-queue-health task-queue-init

task-queue-init-db:
	PYTHONPATH=. procrastinate --app=pinning_service.task_queue.task_queue schema --apply

task-queue-health:
	PYTHONPATH=. procrastinate --app=pinning_service.task_queue.task_queue healthchecks

task-queue-init: task-queue-init-db task-queue-health

task-queue-worker:
	PYTHONPATH=. procrastinate --app=pinning_service.task_queue.task_queue worker


.PHONY: start test test-watch

start:
	uvicorn pinning_service.main:app --reload

test:
	pytest

test-watch:
	ptw

