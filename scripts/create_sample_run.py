import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")

mlflow.set_experiment("opslens-demo")

with  mlflow.start_run(run_name="baseline-training"):
    mlflow.log_param("model_type", "xgboost")
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("batch_size", 64)

    mlflow.log_metric("accuracy", 0.91)
    mlflow.log_metric("loss", 0.24)
    mlflow.log_metric("latency_ms", 125.0)

    mlflow.set_tag("environment", "development")
    mlflow.set_tag("team", "ml-platform")