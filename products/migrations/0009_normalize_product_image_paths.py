from django.db import migrations


def normalize_product_image_paths(apps, schema_editor):
    ProductImage = apps.get_model("products", "ProductImage")

    for image in ProductImage.objects.all().only("uid", "image"):
        image_name = image.image.name
        if image_name.startswith("Product/"):
            image.image.name = "product/" + image_name[len("Product/"):]
            image.save(update_fields=["image"])


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0008_alter_productimage_image"),
    ]

    operations = [
        migrations.RunPython(
            normalize_product_image_paths,
            migrations.RunPython.noop,
        ),
    ]