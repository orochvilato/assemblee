



$(document).ready( function() {
  var db = new loki('sandbox.db');
  // Add a collection to the database
  var votants = db.addCollection('votants');
  var axes;
  $.ajax({
    //url: 'https://cdn.rawgit.com/maxkfranz/3d4d3c8eb808bd95bae7/raw', // wine-and-cheese.json
    url: 'json/scrutin2.json',
    type: 'GET',
    dataType: 'json'
  }).done(function(data) {
    var scrutin = data;
    $('#numeroscrutin').html(scrutin.numero);
    $('#libellescrutin').html(scrutin.libelle);
    scrutin['positions'].forEach(function (p) {
       votants.insert(p);
    });
    selectAxe(0);
  });

  $.ajax({
    //url: 'https://cdn.rawgit.com/maxkfranz/3d4d3c8eb808bd95bae7/raw', // wine-and-cheese.json
    url: 'json/axes.json',
    type: 'GET',
    dataType: 'json'
  }).done(function(data) {
    axes = data;
    for (i=0; i<axes.noms.length; i++) {
      $('#axes').append('<a class="axe waves-effect waves-light btn" n='+i+'>'+axes.noms[i]+'</a> ');
    }
    $('.axe').click(function() {
      var axen = $(this).attr('n');
      selectAxe(axen);

    })

  });
  function selectAxe(axen) {
    var def = axes.defs[axes.noms[axen]];
    $('#vue').empty();
    for (i=0; i<def.items.length; i++) {
      //$('#vue').append('<h4>'+def.items[i][1]+'</h4>');
      var sel = {};
      var cmp = {}

      cmp[def.compare] = def.items[i][0];
      sel[def.field] = cmp
      var results = votants.find(sel);
      console.log(sel,results);
      var stats = { pour:0, contre:0, abstention:0, 'nonVotant':0, absent:0};
      for (j=0; j<results.length;j++) {
        stats[results[j].position] += 1;
      }
      var stats_list =[];
      var positions = ['pour','contre','abstention']
      var icons = { pour:'thumbs-up', contre:'thumbs-down', abstention:'meh', 'nonVotant':'ban', 'absent':'plane'};

      positions.forEach(function(p) {
        if (stats[p]>0) {
          stats_list.push({ position:p, n:stats[p], pct:Math.round(100*stats[p]/results.length), icon:icons[p] });
        }
      });
      stats_list.sort(function(a, b) { return b.n - a.n; });

      var abs = ['nonVotant','absent'];
      abs.forEach(function(p) {
        if (stats[p]>0) {
          stats_list.push({ position:p, n:stats[p], pct:Math.round(100*stats[p]/results.length), icon:icons[p] });
        }
      });
      if (stats_list.length>0) {
        stats_list[0].big = true;
        stats_list[stats_list.length-1].big = true;
        stats_list[stats_list.length-1].last = true;
      }
      var _cercles =  { pour:[], contre:[], abstention:[], 'nonVotant':[], absent:[] };
      results.forEach(function(r) {
        _cercles[r.position].push(r);
      });
      var cercles = [];
      stats_list.forEach(function(s) {
        cercles = cercles.concat(_cercles[s.position]);
      })


      var template = document.getElementById('template').innerHTML;
      Mustache.parse(template);
      var rendered = Mustache.render(template, {titre: def.items[i][1], cercles: cercles, stats:stats_list});
      //Overwrite the contents of #target with the rendered HTML
      $('#vue').append(rendered);
    }
  }
  // Add some documents to the collection

  // Find and update an existing document


});
