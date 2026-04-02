import os
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta
from pendulum import timezone
from docker.types import Mount

KST = timezone("Asia/Seoul")
BASE = os.getenv("BASE_PATH")
# .env 파일의 BASE_PATH 환경변수 사용

default_args = {
    "retries": 2,
    # 실패 시 최대 재시도 횟수
    "retry_delay": timedelta(minutes=3),
    # 재시도 간격 (3분 후 재시도)
}

with DAG(
    dag_id="pipeline",
    default_args=default_args,
    start_date=datetime(2026, 3, 25, tzinfo=KST),
    schedule_interval="0 9 * * *",
    catchup=False,
) as dag:
    crawler = DockerOperator(
        task_id="crawler",
        image="baseball-crawler",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="baseball_default",
        mount_tmp_dir=False,
        mounts=[
            Mount(
                source=f"{BASE}/dataset",
                target="/app/output",
                type="bind",
                # 크롤러가 생성한 CSV를 dataset 폴더에 저장
            )
        ],
    )
    etl = DockerOperator(
        task_id="etl",
        image="baseball-etl",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        network_mode="baseball_default",
        mount_tmp_dir=False,
        mounts=[
            Mount(source=f"{BASE}/dataset", target="/app/dataset", type="bind"),
            Mount(source=f"{BASE}/model",   target="/app/model",   type="bind"),
            Mount(source=f"{BASE}/output",  target="/app/output",  type="bind"),
            # etl 컨테이너가 필요한 폴더 3개 마운트
        ],
        environment={
            "BASE_PATH":    "/app",
            "INPUT_PATH":   "/app/dataset",
            "OUTPUT_PATH":  "/app/output",
            "MODEL_PATH":   "/app/model/win_predictor.pkl",
            "MAPPING_PATH": "/app/dataset/team_info.csv",
            "ENCODING":     "cp949",
            "DB_HOST":      "my-mysql",
            "DB_PORT":      "3306",
            "DB_NAME":      "docker_test_db",
            "DB_USER":      "root",
            "DB_PASSWORD":  "1234",
            # etl.py가 필요로 하는 환경변수 세팅
        },
    )
    crawler >> etl