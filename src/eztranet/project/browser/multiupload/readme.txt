Multiple file upload element (Mootools 1.1 version)
 by Stickman
 http://the-stickman.com
  with thanks to:
	 Luis Torrefranca -- http://www.law.pitt.edu
	 and
	 Shawn Parker & John Pennypacker -- http://www.fuzzycoconut.com
    ...for Safari fixes in the original version

Licence:
 You may use this script as you wish without limitation, however I would 
 appreciate it if you left at least the credit and site link above in 
 place. I accept no liability for any problems or damage encountered 
 as a result of using this script. 

Requires:
 Mootools 1.1 [ http://mootools.net ]
 ...with at least:
  Window.DomReady and its dependencies
  [ Download this release here: http://tinyurl.com/25ksor ]
Supports:
 All browsers supported by Mootools (see Mootools site for details)

Usage:
 See the included example.html for demonstration code.

 Include this file (or the packed version) and your mootools.js release in 
 your HTML file. To  convert a standard file input element into a multiple 
 file input element, add the following code to your HTML:

   window.addEvent('domready', function(){
     new MultiUpload( $( 'my_form' ).my_file_input_element );
   });

 ...where 'my_form' is the ID of your form and 'my_file_input_element' is 
 the name of the file input element to be converted (or use whichever other
 method you prefer for finding the target file input element).

 I've also included a simple CSS file (Stickman.MultiUpload.css) which
 you can include, although it's very basic (see 'Styling the element'),
 below.

Optional parameters:
 There are four optional parameters (null = ignore this parameter):

 - maximum number of files (default = 0)
   An integer to limit the number of files that can be uploaded using the 
   element. A value of zero means 'no limit'.

 - File name suffix template (default '_{id}'
   By default, the script will take the name of the original file input 
   element and append an underscore followed by a number to it, eg. if the 
   input's name is 'file' then the elements will be numbered sequentially: 
   file_0, file_1, file_2... 
   You can change the format of the suffix by passing in a template. This 
   can be any string, but the sequence '{id}' will be replaced by the 
   sequential ID of the element. So if the element is called 'file' and you
   pass in the template '[{id}]' then the elements will be named file[0], 
   file[1], file[2]...
   To remove the suffix entirely, simply pass an empty string.

 - Remove file path (default = false)
   By default, the entire path of the file is shown in the list of files. 
   If you would prefer to show only the file name, set this option to 
   'true'.

 - Remove empty file input element (default = false)
   Because an extra (empty) element is created every time a file is 
   chosen, this means that there will always be one empty file input 
   element when the form is submitted. By default this is submitted with 
   the form (exactly as it would be with a 'normal' file input element, in 
   most browsers) but setting this option to 'true' will cause the element 
   to be disabled  (and therefore ignored) when the form is submitted.

Styling the element
 I didn't spend a lot of time making this look pretty. I've included an
 example CSS file (Stickman.MultiUpload.css) which is very basic but shows
 the parts that make up the element. These are:
  - div.multiupload
    When instaniated, the script places a container DIV around the file
    element, which also includes the files list
  - div.list
    Container DIV for the list of files
  - div.item
    Each item in the files list
  - div.item img
    The delete button image
 If changing the appearance of the element is not enough, you can alter the
 structure of the container and list elements in the initialize() method, 
 or the file list elements in the addRow() method.

Handling the uploaded files
 This is purely a client-side script -- I have not included any code for
 handling the uploaded files when they reach your server. This is because
 I don't know what platform you're using, or what you want to do with the
 files. When I posted the original version of this script, a lot of people 
 went on to submit support code for various platforms. So you might find
 what you need in the comments one of these pages:
  http://tinyurl.com/8yp53
  http://tinyurl.com/wrc8p

Other notes
 Because it's not possible to  set the value of a file input element
 dynamically (for good security reasons), this script works by hiding the 
 file input element when a file is selected, then immediately replacing
 it with a new, empty one. This happens so quickly that it looks as if
 there's only ever one file input element. 
 Although ideally the extra elements would be hidden using the CSS setting
 'display:none', this causes Safari to ignore the element completely when
 the form is submitted. So instead, elements are moved to a position 
 off-screen.
 And no, it's not 'Ajax' -- it doesn't upload the files in the background or
 anything clever like that. Its sole purpose is cosmetic: to remove the 
 need for multiple file input elements in a form.