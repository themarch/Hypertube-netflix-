document.getElementById("watch").addEventListener("click", function(event){
  document.querySelector(".image_video").style = 'filter:grayscale(1);'
  event.stopPropagation();
  var resp = {
      'pal': 'pal'
  };
  $.ajax({
    type: 'POST',
    url: `${window.location}`,
    data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'pal' : 'pal'},
    success: function(data){
      console.log('huhuhuh')
      console.log(data['infos']['ids'])
      bouboule = window.location.pathname
      bouboule = bouboule.split('/')
      bouboule = bouboule[2]
      add = 'http://localhost:3000/play?film=' + data['infos']['ids']+ '&lang=' + data['infos']['lan'] + '&tok=' + data['infos']['token']
      document.location.href=add
      console.log(bouboule)
    }
  });

})
