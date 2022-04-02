notificationBox = document.getElementById('notification_box');
notificationText = document.getElementById('notification_text');
notificationTimeout1 = null;
notificationTimeout2 = null;

async function notificationDisplay(m) {
    
  if (notificationTimeout1 != null) {
    clearTimeout(notificationTimeout1);
    notificationTimeout1 = null;
  }

  if (notificationTimeout2 != null) {
    clearTimeout(notificationTimeout2);
    notificationTimeout2 = null;
  }

  notificationText.innerHTML = m;
  notificationBox.style.display = 'flex';
  notificationBox.style.opacity = 100;
  
  notificationTimeout1 = setTimeout(() => {
    notificationBox.style.opacity = 0;
  }, 3000);
  
  notificationTimeout2 = setTimeout(() => {
    notificationBox.style.display = 'none';
  }, 3250);

}