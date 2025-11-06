"""Initial migration for conversations app."""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('ended', 'Ended'), ('archived', 'Archived')], db_index=True, default='active', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('key_points', models.JSONField(blank=True, default=list)),
                ('sentiment', models.CharField(blank=True, choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative'), ('mixed', 'Mixed')], max_length=20, null=True)),
                ('duration', models.IntegerField(blank=True, help_text='Duration in seconds', null=True)),
                ('embedding', models.JSONField(blank=True, help_text='Conversation embedding for semantic search', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('sender', models.CharField(choices=[('user', 'User'), ('ai', 'AI Assistant')], db_index=True, max_length=10)),
                ('content', models.TextField()),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('embedding', models.JSONField(blank=True, help_text='Message embedding vector', null=True)),
                ('tokens_used', models.IntegerField(default=0, help_text='Token count for API tracking')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='conversations.conversation')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('query_text', models.TextField()),
                ('results_count', models.IntegerField(default=0)),
                ('execution_time', models.FloatField(help_text='Query execution time in seconds')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='search_queries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ConversationAnalysis',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('topics', models.JSONField(default=list, help_text='Extracted topics with confidence scores')),
                ('entities', models.JSONField(default=list, help_text='Named entities and their types')),
                ('intent', models.CharField(blank=True, max_length=100)),
                ('keywords', models.JSONField(default=list, help_text='Important keywords')),
                ('sentiment_scores', models.JSONField(default=dict, help_text='Detailed sentiment analysis')),
                ('action_items', models.JSONField(default=list, help_text='Extracted action items')),
                ('questions_asked', models.JSONField(default=list, help_text='Questions from the conversation')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('conversation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='conversations.conversation')),
            ],
            options={
                'verbose_name_plural': 'Conversation Analyses',
            },
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['conversation', 'created_at'], name='conversations_conver_d5c7f1_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['sender', 'created_at'], name='conversations_sender_a9b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['user', '-started_at'], name='conversations_user_id_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['status', 'user'], name='conversations_status_b3c4d5_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['user', 'status'], name='conversations_user_status_e6f7g8_idx'),
        ),
        migrations.AddIndex(
            model_name='searchquery',
            index=models.Index(fields=['user', '-created_at'], name='conversations_user_created_h9i0j1_idx'),
        ),
        migrations.AddIndex(
            model_name='conversationanalysis',
            index=models.Index(fields=['conversation'], name='conversations_conver_analysis_k2l3m4_idx'),
        ),
    ]