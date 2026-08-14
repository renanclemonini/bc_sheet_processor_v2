from bcsheetsprocessor.service import job_service


class TestJobServiceMemoria:
    def test_status_nao_encontrado(self, ambi_test):
        assert job_service.get_job_status("nao-existe") is None

    def test_set_e_get(self, ambi_test):
        job_service.set_job_status("job-1", {"status": "processing", "progresso": 0})
        status = job_service.get_job_status("job-1")
        assert status["status"] == "processing"
        assert status["progresso"] == 0

    def test_update_progress_mantem_dados(self, ambi_test):
        job_service.set_job_status("job-2", {"status": "processing", "arquivo_original": "a.xlsx"})
        job_service.update_job_progress("job-2", 50)
        status = job_service.get_job_status("job-2")
        assert status["status"] == "processing"
        assert status["progresso"] == 50
        assert status["arquivo_original"] == "a.xlsx"

    def test_overwrite(self, ambi_test):
        job_service.set_job_status("job-3", {"status": "processing"})
        job_service.set_job_status("job-3", {"status": "completed"})
        assert job_service.get_job_status("job-3")["status"] == "completed"

    def test_jobs_isolados(self, ambi_test):
        job_service.set_job_status("job-a", {"status": "processing"})
        assert job_service.get_job_status("job-b") is None

    def test_limpeza_entre_testes(self, ambi_test):
        assert job_service.get_job_status("job-a") is None