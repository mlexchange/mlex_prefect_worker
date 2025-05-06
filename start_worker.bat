@echo off
REM Load environment variables from .env file
for /F "tokens=*" %%A in (.env) do set %%A

REM Export environment variables
set PREFECT_WORK_DIR=%PREFECT_WORK_DIR%

REM Configure Prefect
prefect config set PREFECT_API_URL=%PREFECT_API_URL%

REM Create work pool
prefect work-pool create mlex_pool --type "process"
prefect work-pool set-concurrency-limit mlex_pool %PREFECT_WORK_POOL_CONCURRENCY%
prefect deploy --all

REM Start worker
prefect worker start --pool mlex_pool --limit %PREFECT_WORKER_LIMIT% --with-healthcheck