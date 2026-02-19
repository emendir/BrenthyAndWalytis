from threading import Thread
import docker
import os
from .brenthy_docker import BrenthyDocker


def get_logs_and_delete_docker(
    docker_container: BrenthyDocker,
    log_files: list[str],
    log_dirs: list[str],
) -> None:
    """Download logs from then delete docker containers."""
    for log_file in log_files:
        for report_dir in log_dirs:
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            download_path = os.path.join(
                report_dir,
                f"{docker_container.container_name}-"
                f"{os.path.basename(log_file)}",
            )
            try:
                docker_container.download(
                    log_file,
                    download_path,
                )
            except docker.errors.NotFound:
                pass
    docker_container.delete()


def get_logs_and_delete_dockers(
    docker_containers: list[BrenthyDocker],
    log_files: list[str],
    log_dirs: list[str],
) -> None:
    # Terminate Docker containers and our test brenthy instance in parallel
    termination_threads = []
    # start terminating docker containers
    for docker_container in docker_containers:
        if not docker_container:
            continue
        termination_threads.append(
            Thread(
                target=get_logs_and_delete_docker,
                args=(docker_container, log_files, log_dirs),
            )
        )
        termination_threads[-1].start()
    # terminate our own brenthy instance
    # wair till all docker containers are terminated
    for thread in termination_threads:
        thread.join()
