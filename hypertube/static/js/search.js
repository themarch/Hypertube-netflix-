function display_film(data){
  console.log(data)
        variole = document.querySelector('.row')
        sort = ""
        data['movie'].forEach(element => {
          sort = sort + '<div class="column">\
          <div class="content">\
            <div class="floutage">\
              <h3 class="texte_centre">' +  element[7] + ' / 10</h3>\
              <img class="etoile" src="../media/etoile.png">'
                if (element[15] == false){
                  sort = sort + 
                   '<a href="http://localhost:8000/video/' + element[0] + '"><img class="gris1234" src="'+ element[3] + '" alt="' + element[1] + '" style="width:100%"></a>'
                } else {
                  sort = sort +
                  '<a href="http://localhost:8000/video/serie/' + element[0] + '"><img class="gris1234"\ src="' + element[3] + '" alt="' + element[1] + '" style="width:100%"></a>'
                }
              sort = sort + 
              '<button class="button button3">View Details</button>\
             </div>\
            <h5 class="titre">' + element[1] + '</h5>\
            <span class="hidden-xs icon-star"></span>\
          </div>\
        </div>'})
      variole.innerHTML = sort
}

function find_filter(){
  var sel1 = document.getElementById("sel1").value;
  if (!sel1 || sel1 == ''){
    sel1 = 'rate'
  }
  var genre = document.getElementById("genre").value;
  if (!genre || genre == '' || genre == 'ALL'){
    genre = '|'
  }
  var notes = (document.getElementById("notes").value);
  if (!notes || notes == '' || notes == 'ALL'){
    notes = '0-10'
  }
  notes = notes.split('-')
  var dates = (document.getElementById("dates").value);
  if (!dates || dates == '' || dates == 'ALL'){
    dates = '1970-2020'
  }
  dates = dates.split('-')
  var tri = [sel1, genre, notes[0], notes[1], dates[0], dates[1]]
  tri = tri.join(' ')
  console.log(tri)
  return (tri)
}

function find_filterS(){
  var sel1 = document.getElementById("sel1S").value;
  if (!sel1 || sel1 == ''){
    sel1 = 'rate'
  }
  var genre = document.getElementById("genreS").value;
  if (!genre || genre == '' || genre == 'ALL'){
    genre = '|'
  }
  var notes = (document.getElementById("notesS").value);
  if (!notes || notes == '' || notes == 'ALL'){
    notes = '0-10'
  }
  notes = notes.split('-')
  var dates = (document.getElementById("datesS").value);
  if (!dates || dates == '' || dates == 'ALL'){
    dates = '1970-2020'
  }
  dates = dates.split('-')
  var tri = [sel1, genre, notes[0], notes[1], dates[0], dates[1]]
  tri = tri.join(' ')
  console.log(tri)
  return (tri)
}
if (window.location.pathname == '/'){
  document.getElementById("sel1").addEventListener("change", function(){ 
      var val = find_filter()
      var resp = {
          'val': val
      };
      $.ajax({
        type: 'POST',
        url: `${window.location}`,
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
        success: function(data){
          display_film(data)
        }
      });
    });

    document.getElementById("genre").addEventListener("change", function(){ 
      var val = find_filter()
      var resp = {
          'val': val
      };
      $.ajax({
        type: 'POST',
        url: `${window.location}`,
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
        success: function(data){
          display_film(data)
        }
      });
    });

    document.getElementById("notes").addEventListener("change", function(){ 
      var val = find_filter()
      var resp = {
          'val': val
      };
      $.ajax({
        type: 'POST',
        url: `${window.location}`,
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
        success: function(data){
          display_film(data)
        }
      });
    });
      document.getElementById("dates").addEventListener("change", function(){ 
        var val = find_filter()
        var resp = {
            'val': val
        };
        $.ajax({
          type: 'POST',
          url: `${window.location}`,
          data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
          success: function(data){
            display_film(data)
          }
        });
      });
    }
    console.log(window.location.pathname)
    if (window.location.pathname == '/search/'){
      console.log('tutu')
    document.getElementById("sel1S").addEventListener("change", function(){ 
      var val = find_filterS()
      var resp = {
          'val': val
      };
      $.ajax({
        type: 'POST',
        url: `${window.location}`,
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
        success: function(data){
          display_film(data)
        }
      });
    });

    document.getElementById("genreS").addEventListener("change", function(){ 
      var val = find_filterS()
      var resp = {
          'val': val
      };
      $.ajax({
        type: 'POST',
        url: `${window.location}`,
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
        success: function(data){
          display_film(data)
        }
      });
    });

    document.getElementById("notesS").addEventListener("change", function(){ 
      var val = find_filterS()
      var resp = {
          'val': val
      };
      $.ajax({
        type: 'POST',
        url: `${window.location}`,
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
        success: function(data){
          display_film(data)
        }
      });
    });

    document.getElementById("datesS").addEventListener("change", function(){ 
      var val = find_filterS()
      var resp = {
          'val': val
      };
      $.ajax({
        type: 'POST',
        url: `${window.location}`,
        data: {csrfmiddlewaretoken: window.CSRF_TOKEN, 'val' : val},
        success: function(data){
          display_film(data)
        }
      });
    });
  }

    