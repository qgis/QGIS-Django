// Replace the date with local timezone

$(".user-timezone").each(function (i) {
  let localDate = toUserTimeZone($(this).text());
  $(this).text(localDate);
})

function toUserTimeZone(date) {
  try {
    date = new Date(date);
    let options = {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
      timeZoneName: 'short'
    }
    return date.toLocaleDateString([], options);
  } catch (e) {
    return date;
  }
}

