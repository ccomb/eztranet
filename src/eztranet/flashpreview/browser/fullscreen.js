/*
 *  * Default FlowPlayer fullscreen opener.
 *   * http://flowplayer.org
 *    */
 

function flowPlayerOpenFullScreen(config) {
  var winWidth = window.screen.availWidth;
  var winHeight = window.screen.availHeight;
  var fullScreenWindow = window.open('/@@/fullscreen.html?config='+config, 'FlowPlayer', 'left=0,top=0,width='+winWidth+',height='+winHeight+',status=no,resizable=yes');
}

function flowPlayerExitFullScreen(config) {
  self.close();
}

