#Create a bucket
resource "aws_s3_bucket" "b1" {
  bucket = "s3-terraform-bucket1"
  tags = {
    Name = "My bucket"
    }
}
