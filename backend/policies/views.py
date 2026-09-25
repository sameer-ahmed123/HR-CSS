from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from policies.models import PolicyCategory, Policy, PolicyAcknowledgement
from policies.serializers import PolicyCategorySerializer, PolicyListSerializer, PolicyDetailSerializer, PolicyAcknowledgementSerializer
from django.db.models import Q, Count


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def policy_category_list_create_view(request):
    if request.method == "GET":
        policy_category_qs = PolicyCategory.objects.filter(is_active=True).annotate(total_policies=Count("policies"))
        serializer = PolicyCategorySerializer(policy_category_qs, many=True)
        return Response(serializer.data, status=200)

    if request.method == "POST":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response({"error": "only admin or Hr can access policy related objects"})
        serializer = PolicyCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def policy_list_create_view(request):
    if request.method == "GET":
        if request.user.role not in ["ADMIN", "HR"]:
            policy_qs = Policy.objects.select_related(
                "category").filter(is_active=True)
        else:
            policy_qs = Policy.objects.select_related(
                "category").all()
        category_param = request.query_params.get("category")
        search_param = request.query_params.get("search")
        mandatory_param = request.query_params.get("mandatory")

        if category_param:
            policy_qs = policy_qs.filter(category=category_param)
        if search_param:
            policy_qs = policy_qs.filter(
                Q(title__icontains=search_param) | Q(content__icontains=search_param))
        if mandatory_param is not None:
            # Converts string query parameter ('true'/'false') to a boolean
            is_mandatory = mandatory_param.lower() in ['true', '1', 't']
            policy_qs = policy_qs.filter(is_mandatory=is_mandatory)

        serializer = PolicyListSerializer(
            policy_qs, many=True, context={"request": request})
        return Response(serializer.data, status=200)

    if request.method == "POST":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response({"error": "only admin or Hr can access policy related objects"})
        serializer = PolicyDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def policy_detail_view(request, pk):
    policy = get_object_or_404(Policy.objects.select_related("category"),id=pk)

    if request.method == "GET":
        serializer = PolicyDetailSerializer(policy)
        return Response(serializer.data, status=200)

    if request.method in ["PUT", "PATCH"]:
        if request.user.role not in ["ADMIN", "HR"]:
            return Response({"error": "only admin or Hr can access policy related objects"})
        serializer = PolicyDetailSerializer(
            policy, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        if request.user.role not in ["ADMIN", "HR"]:
            return Response({"error": "only admin or Hr can access policy related objects"})
        policy.delete()
        return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def policy_acknowledge_view(request, pk):
    policy = get_object_or_404(Policy, id=pk)
    if PolicyAcknowledgement.objects.filter(user=request.user, policy=policy).exists():
        return Response({"detail": "Policy already acknowledged."}, status=400)
    serializer = PolicyAcknowledgementSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(policy=policy, user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_acknowledgments(request):
    my_ack = PolicyAcknowledgement.objects.filter(user=request.user)
    serializer = PolicyAcknowledgementSerializer(my_ack, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pending_acknowledgements(request):
    pending_ack = Policy.objects.filter(is_active=True).exclude(
        acknowledgements__user=request.user).select_related("category").distinct()
    serializer = PolicyListSerializer(
        pending_ack, many=True, context={"request": request})
    return Response(serializer.data, status=200)
