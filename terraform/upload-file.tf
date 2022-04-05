# Upload an object
resource "aws_s3_object" "file_upload" {
for_each = fileset("myfiles/", "*")
bucket = aws_s3_bucket.b1.id
key = each.value
source = "myfiles/${each.value}"
etag = filemd5("myfiles/${each.value}")
}
