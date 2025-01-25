

run_backend:
	@echo "Running backend..."
	cd backend && uvicorn app.main:app --reload

run_frontend:
	@echo "Running frontend..."
	cd frontend && npm run dev