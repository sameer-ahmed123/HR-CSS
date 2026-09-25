from rest_framework import serializers
from documents.models import *


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTypeConfig
        fields = '__all__'


class DocumentTemplateSerializer(serializers.ModelSerializer):
    document_type_name = serializers.CharField(
        source='document_type.name',
        read_only=True
    )

    class Meta:
        model = DocumentTemplate
        fields = [
            'id',
            'document_type',
            'document_type_name',
            'title',
            'body_content',
            'include_letterhead',
            'letterhead_image',
            'footer_text',
            'updated_at',
        ]


class DocumentRequestSerializer(serializers.ModelSerializer):
    requested_by_email = serializers.CharField(
        source='requested_by.email',
        read_only=True
    )
    assigned_hr_email = serializers.CharField(
        source='assigned_hr.email',
        read_only=True
    )
    document_type_name = serializers.CharField(
        source='document_type.name',
        read_only=True
    )

    class Meta:
        model = DocumentRequest
        fields = [
            'id',
            'requested_by',
            'requested_by_email',
            'document_type',
            'document_type_name',
            'purpose',
            'needed_by',
            'expected_completion_date',
            'status',
            'rejection_reason',
            'assigned_hr',
            'assigned_hr_email',
            'reference_number',
            'file_version',
            'manual_upload',
            'generated_file',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'requested_by',
            'assigned_hr',
            'status',
            'expected_completion_date',
            'rejection_reason',
            'reference_number',
            'file_version',
            'manual_upload',
            'generated_file'
        ]


class DocumentRequestDetailSerializer(serializers.ModelSerializer):
    requested_by_email = serializers.CharField(
        source='requested_by.email',
        read_only=True
    )
    assigned_hr_email = serializers.CharField(
        source='assigned_hr.email',
        read_only=True
    )
    document_type_name = serializers.CharField(
        source='document_type.name',
        read_only=True
    )

    class Meta:
        model = DocumentRequest
        fields = [
            'id',
            'requested_by',
            'requested_by_email',
            'document_type',
            'document_type_name',
            'purpose',
            'needed_by',
            'expected_completion_date',
            'status',
            'rejection_reason',
            'assigned_hr',
            'assigned_hr_email',
            'reference_number',
            'file_version',
            'manual_upload',
            'generated_file',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'requested_by',
            'expected_completion_date',
            'assigned_hr',
            'status',
            'rejection_reason',
            'reference_number',
            'file_version',
            'manual_upload',
        ]
