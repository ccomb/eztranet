function toggle_image_size(size1,size2) {
    img = document.getElementById("main_image")
    if (img.width == size1) { img.width= size2 }
    else if (img.width == size2) { img.width= size1 }
}