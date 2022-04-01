notificationBox = document.getElementById('notification_box');
notificationText = document.getElementById('notification_text');
notificationDisplayTimeout = null;

async function notificationDisplay(m) {
    
  if (notificationDisplayTimeout != null) {
    clearTimeout(notificationDisplayTimeout)
    notificationDisplayTimeout = null
  }

  notificationText.innerHTML = m;
  notificationBox.style.opacity = 100;
  
  notificationDisplayTimeout = setTimeout(() => {
    notificationBox.style.opacity = 0;
  }, 3000);
  
}