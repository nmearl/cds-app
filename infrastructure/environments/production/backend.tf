terraform {
  backend "local" {
    path = "../../.terraform-state/production/terraform.tfstate"
  }
}
