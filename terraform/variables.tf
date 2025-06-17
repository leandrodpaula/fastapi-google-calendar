variable "project_id" {
  description = "The Google Cloud project ID."
  type        = string
}

variable "region" {
  description = "The GCP region for deployment."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name for the Cloud Run service."
  type        = string
  default     = "event-manager-api"
}

variable "image_name" {
  description = "Name of the Docker image in GCR or Artifact Registry."
  type        = string
  default     = "event-manager-api-image" # This would typically be built by a CI/CD pipeline
}

variable "container_port" {
  description = "The port the container exposes."
  type        = number
  default     = 8000
}

variable "max_instance_count" {
  description = "Maximum number of instances for Cloud Run service scaling."
  type        = number
  default     = 2 # Default to a small number for cost control
}

variable "cloud_run_invoker_role_members" {
  description = "List of members to grant the Cloud Run Invoker role. Use ['allUsers'] for public access."
  type        = list(string)
  default     = ["allUsers"]
}
