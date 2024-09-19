API URL Configuration
# QGIS Django API Documentation

The `urlpatterns` list routes URLs to views. For more information please see:
[https://docs.djangoproject.com/en/3.2/topics/http/urls/](https://docs.djangoproject.com/en/3.2/topics/http/urls/)

## Endpoints

### Resources
- **URL:** `/resources/`
- **Method:** `GET`
- **View:** `ResourceAPIList.as_view()`
- **Name:** `resource-list`
- **Description:** Retrieves a list of all resources.

### Resource by UUID
- **URL:** `/resource/<uuid:uuid>/`
- **Method:** `GET`
- **View:** `ResourceAPIDownload.as_view()`
- **Name:** `resource-download`
- **Description:** Downloads a specific resource identified by UUID.

### Create Resource
- **URL:** `/resource/create`
- **Method:** `POST`
- **View:** `ResourceCreateView.as_view()`
- **Name:** `resource-create`
- **Description:** Creates a new resource.
- **Request example with cURL:**
    ```sh
    curl --location 'http://localhost:62202/api/v1/resource/create' \
    --header 'Authorization: Bearer <my_token>' \
    --form 'file=@"path/to/the/file.zip"' \
    --form 'thumbnail_full=@"path/to/the/thumbnail.png"' \
    --form 'name="My model"' \
    --form 'description="Little description"' \
    --form 'tags="notag"' \
    --form 'resource_type="model"'
    ```

