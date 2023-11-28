// Replace the date with local timezone

$(".user-timezone").each(function (i) {
  let localDate = toUserTimeZone($(this).text());
  $(this).text(localDate);
})

$(".short-user-timezone").each(function (i) {
  let localDate = toUserTimeZone($(this).text(), false);
  $(this).text(localDate);
})

function toUserTimeZone(date, withTime=true) {
  try {
    date = new Date(date);
    let options = {
      year: 'numeric', month: 'short', day: 'numeric'
    }
    if (withTime) {
      options['hour'] = '2-digit'
      options['minute'] = '2-digit'
      options['timeZoneName'] = 'short'
    }
    const diffInDays = moment().diff(moment(date), 'days');

    if (diffInDays <= 1 && !withTime) {
      const distance = moment(date).fromNow();
      return distance
    }
    return date.toLocaleDateString([], options);
  } catch (e) {
    return date;
  }
}

