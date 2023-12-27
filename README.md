## How to Use
Save the credentials in the following environment variable
bhoo_username
bhoo_password

## Functions
```
    from bhoobotapi.search import Bhoonidhi
    from datetime import datetime

    instance = Bhoonidhi()
    date = datetime.now()
    # To check the cart items
    cart_items = instance.view_cart(date)
    # To download all the data in the cart
    instance.download_cart(date)
```
