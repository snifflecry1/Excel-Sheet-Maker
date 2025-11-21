# 🧩 Morta Coding Challenge – “Mini Spreadsheet”

  

Welcome!

  

Your task is to build a single-page spreadsheet app where users can create, view, and edit an online spreadsheet. You should also be able to export the spreadsheet to CSV using an asynchronous celery task.

  

This should be done using Flask + Postgres + Celery + Redis (backend) and React (frontend) — all runnable via Docker Compose.



  

## 🕒 Tools

  
 

You may use AI freely — just note significant assists in your submission.

  

Focus on clarity, maintainability, and functionality over completeness.

  


  

## 🎯 Requirements

  

### Core Features

- Create a new spreadsheet
- View a spreadsheet as a grid
- Edit cell values inline
- Persist data in Postgres via a Flask REST API
- No authentication required
- Asynchronous CSV Export using Celery + Redis

  

### Nice-to-Have (optional)

- Rename spreadsheet
- Add/remove rows or columns
- Simple formula support (=A1+B2)
- CSV import  



  

## 🧱 Tech Stack

  

**Backend:** Flask + SQLAlchemy + Postgres

**Frontend:** React (Vite or CRA)

**Database:** PostgreSQL

**Containerization:** Docker + docker-compose

  

You may use any UI, state management, or helper libraries.

  
  

## 📦 Running the App

  

1️⃣ Clone the repo

```bash

git  clone <your-repo-url>

cd <repo-name>

```

  

2️⃣ Run with Docker

```bash

docker-compose  up  --build

```

This should start:

  

- Backend: http://localhost:5000

- Frontend: http://localhost:3000

- Postgres: localhost:5432

  

Your `docker-compose.yml` should define all services (backend, celery, redis, frontend, db). 


  

## 🧰 Deliverables

  

- [ ] Working app runnable via `docker-compose up`

- [ ] A short **Implementation notes** section explaining: tech choices, any deviations from this README, AI usage and future improvements if given more time



  

## ✅ Evaluation Criteria

  

- Functional correctness

- Code structure and clarity

- API & data model design

- UI/UX quality

- Developer experience (easy to run and understand)

- Documentation

  


## 🧠 Tips

  

- Keep scope small but solid

- Use environment variables for configuration (`.env`).

- Handle errors and invalid inputs gracefully.

- Write at least one small test (backend or frontend).






# Notes

- To run the app just run 

```bash

docker-compose  up  --build

```

- To run the small tests for some of the views in the app run

```bash
docker compose run --rm spreadsheet_tests
```

All documentation on how the design was implemented is in DESIGN.md at root


