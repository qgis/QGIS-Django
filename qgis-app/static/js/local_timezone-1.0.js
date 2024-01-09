// Replace the date with local timezone

$(".user-timezone").each(function (i) {
  let localDate = toUserTimeZone($(this).text());
  $(this).text(localDate);
})

$(".user-timezone-short").each(function (i) {
  let localDate = toUserTimeZone($(this).text(), withTime=false);
  $(this).text(localDate);
})

$(".user-timezone-short-naturalday").each(function (i) {
  let localDate = toUserTimeZone($(this).text(), withTime=false, isNaturalDay=true);
  $(this).text(localDate);
})

function toUserTimeZone(date, withTime=true, isNaturalDay=false) {
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

    if (diffInDays <= 1 && isNaturalDay) {
      const distance = moment(date).fromNow();
      return distance
    }
    return date.toLocaleDateString([], options);
  } catch (e) {
    return date;
  }
}

