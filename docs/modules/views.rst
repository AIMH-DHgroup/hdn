Views
======

A view function, or view for short, is a Python function that takes a Web request and returns a Web response. 
This response can be the HTML contents of a Web page, or a redirect, or a 404 error, or an XML document, or an image . . . 
or anything, really. The view itself contains whatever arbitrary logic is necessary to return that response. 
This code can live anywhere you want, as long as it’s on your Python path. There’s no other requirement–no “magic,” so to speak. 
For the sake of putting the code somewhere, the convention is to put views in a file called views.py, placed in your project or application directory.

.. automodule:: annotation.views
   :members:
   :undoc-members: