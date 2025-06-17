terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0" # Specify a version constraint
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloud_run_v2_service" "default" {
  name     = var.service_name
  location = var.region

  template {
    scaling {
      max_instance_count = var.max_instance_count
      // min_instance_count = 0 # Default, can be set if needed
    }

    containers {
      image = "gcr.io/${var.project_id}/${var.image_name}:latest" # Assumes GCR, adjust if Artifact Registry
      ports {
        container_port = var.container_port
      }

      # Optional: Environment variables
      # env {
      #   name  = "DATABASE_URL"
      #   value = "your-database-url-here" # Or from a secret manager
      # }
      # env {
      #   name = "GCP_PROJECT" # Example if app needs project ID explicitly
      #   value = var.project_id
      # }

      # Optional: Resource limits
      # resources {
      #   limits = {
      #     cpu    = "1000m" # 1 CPU
      #     memory = "512Mi"
      #   }
      #   # startup_cpu_boost = true # For CPU intensive startup
      # }
    }

    # Optional: Execution environment (gen1 or gen2)
    # execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    # Optional: Service account for the Cloud Run revision
    # service_account = "your-service-account-email@${var.project_id}.iam.gserviceaccount.com"
  }

  # Optional: Traffic splitting, tags, etc.
  # traffic {
  #   type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  #   percent = 100
  # }

  lifecycle {
    ignore_changes = [
      # If image is updated frequently by CI/CD using :latest tag,
      # Terraform might not detect changes unless the image digest changes explicitly in config.
      # This depends on how image updates are managed.
      # template[0].containers[0].image,
    ]
  }
}

# Make the Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "invoker" {
  location = google_cloud_run_v2_service.default.location
  name     = google_cloud_run_v2_service.default.name
  project  = google_cloud_run_v2_service.default.project
  role     = "roles/run.invoker"
  member   = "allUsers" # For public access as per requirement

  # If you want to restrict to specific users/service accounts, change 'member'
  # For example:
  # member = "serviceAccount:your-caller-sa@${var.project_id}.iam.gserviceaccount.com"

  # If var.cloud_run_invoker_role_members is used (more flexible):
  # count  = length(var.cloud_run_invoker_role_members)
  # member = var.cloud_run_invoker_role_members[count.index]
  # This would create multiple iam_member resources if list has multiple entries.
  # For a single "allUsers" or a specific SA, direct assignment is simpler.
}

# Note: If using Artifact Registry instead of GCR, the image path would be:
# "${var.region}-docker.pkg.dev/${var.project_id}/${var.image_repository_name}/${var.image_name}:latest"
# where image_repository_name would be another variable for the AR repository name.
# For simplicity, GCR path is used as per common examples. GCR is being phased out in favor of AR.
# The `gcr.io/${var.project_id}/...` path still works for GCR or GCR-domain Artifact Repositories.
