jQuery.fn.ratings = function(stars, initialRating) {

  //Save  the jQuery object for later use.
  var elements = this;
  
  //Go through each object in the selector and create a ratings control.
  return this.each(function() {
  
    //Make sure intialRating is set.
    if(!initialRating)
      initialRating = 0;
      
    //Save the current element for later use.
    var containerElement = this;
    
    //grab the jQuery object for the current container div
    var container = jQuery(this);
    
    //Create an array of stars so they can be referenced again.
    var starsCollection = Array();
    
    //Save the initial rating.
    containerElement.rating = initialRating;
    
    //Set the container div's overflow to auto.  This ensure it will grow to
    //hold all of its children.
    container.css('overflow', 'auto');
    
    //create each star
    for(var starIdx = 0; starIdx < stars; starIdx++) {
      
      //Create a div to hold the star.
      var starElement = document.createElement('div');
      
      //Get a jQuery object for this star.
      var star = jQuery(starElement);
      
      //Store the rating that represents this star.
      starElement.rating = starIdx + 1;
      
      //Add the style.
      star.addClass('jquery-ratings-star');
      
      //Add the full css class if the star is beneath the initial rating.
      // The last star will depend on the decimal left
      if(starIdx < initialRating) {
        let ratingDiff = initialRating - starIdx
        if (ratingDiff > 0 && ratingDiff <= 0.3) {
          star.addClass('jquery-ratings-quarter');
        }
        else if (ratingDiff > 0.3 && ratingDiff <= 0.6) {
          star.addClass('jquery-ratings-half');
        }
        else if (ratingDiff > 0.6 && ratingDiff <= 0.9) {
          star.addClass('jquery-ratings-half-and-quarter');
        }
        else {
          star.addClass('jquery-ratings-full');
        }
      }
      
      //add the star to the container
      container.append(star);
      starsCollection.push(star);
      
      //hook up the click event
      star.click(function() {
        //When clicked, fire the 'ratingchanged' event handler.  Pass the rating through as the data argument.
        elements.triggerHandler("ratingchanged", {rating: this.rating});
        containerElement.rating = this.rating;
      });
      
      star.mouseenter(function() {
        //Highlight selected stars.
        for(var index = 0; index < this.rating; index++) {
          starsCollection[index].removeClass('jquery-ratings-half-and-quarter');
          starsCollection[index].removeClass('jquery-ratings-half');
          starsCollection[index].removeClass('jquery-ratings-quarter');
          starsCollection[index].addClass('jquery-ratings-full');
        }
        //Unhighlight unselected stars.
        for(var index = this.rating; index < stars; index++) {
          starsCollection[index].removeClass('jquery-ratings-full');
          starsCollection[index].removeClass('jquery-ratings-half-and-quarter');
          starsCollection[index].removeClass('jquery-ratings-half');
          starsCollection[index].removeClass('jquery-ratings-quarter');
        }
      });
      
      container.mouseleave(function() {
        //Highlight selected stars.
        for(var index = 0; index < containerElement.rating; index++) {
          let ratingDiff = containerElement.rating - index
          if (ratingDiff > 0 && ratingDiff <= 0.3) {
            starsCollection[index].addClass('jquery-ratings-quarter');
          }
          else if (ratingDiff > 0.3 && ratingDiff <= 0.6) {
            starsCollection[index].addClass('jquery-ratings-half');
          }
          else if (ratingDiff > 0.6 && ratingDiff <= 0.9) {
            starsCollection[index].addClass('jquery-ratings-half-and-quarter');
          }
          else {
            starsCollection[index].addClass('jquery-ratings-full');
          }
        }
        //Unhighlight unselected stars.
        for(var index = Math.floor(containerElement.rating); index < stars ; index++) {
          starsCollection[index].removeClass('jquery-ratings-full');
        }
      });
    }
  });
};