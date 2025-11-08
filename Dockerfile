FROM node:20 AS build
WORKDIR /app
RUN npm install -g @angular/cli
COPY frontend/ .
RUN npm install
RUN npm run build --prod

FROM python:3.11-slim
WORKDIR /app
RUN mkdir -p /app/data
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/main.py .
EXPOSE 8000
COPY --from=build /app/dist/strichliste/browser/ ./static/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

