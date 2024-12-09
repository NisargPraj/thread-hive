# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceHealth",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("service_name", models.CharField(max_length=100, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("healthy", "Healthy"),
                            ("degraded", "Degraded"),
                            ("down", "Down"),
                        ],
                        default="healthy",
                        max_length=20,
                    ),
                ),
                ("last_check", models.DateTimeField(auto_now=True)),
                ("last_successful_check", models.DateTimeField(null=True)),
                ("error_message", models.TextField(blank=True, null=True)),
                ("response_time", models.FloatField(null=True)),
            ],
            options={
                "verbose_name_plural": "Service health statuses",
            },
        ),
        migrations.CreateModel(
            name="ServiceMetrics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("service_name", models.CharField(max_length=100)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("cpu_usage", models.FloatField(null=True)),
                ("memory_usage", models.FloatField(null=True)),
                ("request_count", models.IntegerField(default=0)),
                ("error_count", models.IntegerField(default=0)),
                ("average_response_time", models.FloatField(null=True)),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.AddIndex(
            model_name="servicemetrics",
            index=models.Index(
                fields=["service_name", "timestamp"],
                name="api_service_service_1f4897_idx",
            ),
        ),
        migrations.DeleteModel(
            name="BlockedPost",
        ),
        migrations.DeleteModel(
            name="Report",
        ),
        migrations.DeleteModel(
            name="UserWarning",
        ),
    ]
