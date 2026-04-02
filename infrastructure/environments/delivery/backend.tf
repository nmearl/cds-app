terraform {
  backend "local" {
    path = "../../.terraform-state/delivery/terraform.tfstate"
  }
}
