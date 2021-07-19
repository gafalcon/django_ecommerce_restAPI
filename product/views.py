from django.shortcuts import Http404
from django.db.models import Q

from rest_framework import authentication, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Product, Category, Review
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer


# Create your views here.
class LatestProductsList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()[:4]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetail(APIView):
    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.filter(
                category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class CategoryDetail(APIView):
    def get_object(self, category_slug):
        try:
            return Category.objects.get(slug=category_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, format=None):
        cat = self.get_object(category_slug)
        serializer = CategorySerializer(cat)
        return Response(serializer.data)


@api_view(['POST'])
def search(request):

    query = request.data.get('query', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query))
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    else:
        return Response({"products": []})


class ProductReviews(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_reviews(self, product_slug):
        try:
            return Review.objects.filter(product__slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        reviews = self.get_reviews(product_slug)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, category_slug, product_slug):
        serializer = ReviewSerializer(data=request.data)
        product = Product.objects.filter(
            category__slug=category_slug).get(slug=product_slug)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response({})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
