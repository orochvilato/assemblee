var db = new loki('sandbox.db');
// Add a collection to the database
var votants = db.addCollection('votants');
var axes;
var filtres_axes=[];
var scrutin;
var current_axe = 0;

var loadScrutin= function(s) {
  $.ajax({
    //url: 'https://cdn.rawgit.com/maxkfranz/3d4d3c8eb808bd95bae7/raw', // wine-and-cheese.json
    url: 'json/scrutin'+s+'.json?t='+Date.now(),
    type: 'GET',
    dataType: 'json'
  }).done(function(data) {
    votants.clear();
    scrutin = data;
    $('#noscrutin').html(scrutin.numero);
    $('#libellescrutin').html(scrutin.libelle);
    scrutin['positions'].forEach(function (p) {
       votants.insert(p);
    });
    selectAxe(current_axe);
  });
}
var selectAxe = function(axen) {
    var def = axes.defs[axes.noms[axen]];
    current_axe = axen;
    $('#vue').empty();
    for (var i=0; i<def.items.length; i++) {
      //$('#vue').append('<h4>'+def.items[i][1]+'</h4>');
      var sel = {};
      var cmp = {}





      cmp[def.compare] = def.items[i][0];
      sel[def.field] = cmp
      var req = { '$and':[sel]};
      for (var a=0; a<axes.noms.length; a++) {
        var axereq = {'$or':[]};
        var adef = axes.defs[axes.noms[a]];
        var flt = false;
        for (var it=0; it<filtres_axes[a].length; it++) {
          if (filtres_axes[a][it] == true && a!=axen) {
            flt = true;
            var fsel = {};
            var fcmp = {};

            fcmp[adef.compare] = adef.items[it][0];
            fsel[adef.field] = fcmp
            axereq['$or'].push(fsel);
          }
        }
        if (flt==true) {
          req['$and'].push(axereq);
        }
      }
      var results = votants.find(req);
      if (results.length>0) {
        var stats = { pour:0, contre:0, abstention:0, 'nonVotant':0, absent:0};
        for (var j=0; j<results.length;j++) {
          stats[results[j].position] += 1;
        }
        var stats_list =[];

        var positionsVotants = ['pour','contre','abstention'];
        var icons = { pour:'thumbs-up', contre:'thumbs-down', abstention:'meh-o', 'nonVotant':'ban', 'absent':'plane'};
        var libelles = { pour:'votes pour', contre:'votes contre', abstention:'abstention', 'nonVotant':'non votants (justifiés)', 'absent':'absents'};
        var item_stats =  { n: results.length, pct: Math.round(100*(results.length/scrutin.positions.length))};
        var nvotants = results.length - stats['absent'] - stats['nonVotant']
        positionsVotants.forEach(function(p) {
          if (stats[p]>0) {
            stats_list.push({ libelle:libelles[p], position:p, n:stats[p], pct:Math.round(100*stats[p]/nvotants), icon:icons[p] });
          }
        });
        stats_list.sort(function(a, b) { return b.n - a.n; });

        stats_list.push({ libelle:libelles['absent'], position:'absent', big:true,n:stats['absent'], absent:true, pct:Math.round(100*stats['absent']/results.length), icon:icons['absent'] });
        if (stats['nonVotant']>0) {
            stats_list.push({ libelle:libelles['nonVotant'], position:'nonVotant', n:stats['nonVotant'], absent:true, pct:Math.round(100*stats['nonVotant']/results.length), icon:icons['nonVotant'] });
        }


        if (stats_list.length>0) {
          stats_list[0].big = true;
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
        var rendered = Mustache.render(template, {filtered:filtres_axes[axen][i], axe:axen,i:i,hidechart:def.hidechart, key: def.items[i][0], titre: def.items[i][1], cercles: cercles, stats:stats_list, item_stats:item_stats});

        $('#vue').append(rendered);

      }

      if (!def.hidechart && results.length>0) {
        var ctx = document.getElementById("donut"+i);
        var randomScalingFactor = function() {
         return Math.round(Math.random() * 100);
        };

        var myChart = new Chart(ctx, {
         type: 'doughnut',
         data: {
             datasets: [{
                 data: [
                     stats['pour'],
                     stats['contre'],
                     stats['abstention'],
                     stats['nonVotant'],
                     stats['absent']
                 ],
                 backgroundColor: [
                     "green",
                     "red",
                     "grey",
                     "lightgrey",
                     "lightgrey",
                 ],
                 label: 'Dataset 1'
             }],
             labels:['Pour','Contre','Abstention','Non votant','Absent']

         },
         options: {
             responsive: true,
             legend: {
                 display: false
             },
             title: {
                 display: true,
                 text: 'Répartition par position de vote'
             },
             animation: {
                 animateScale: false,
                 animateRotate: false,
             }
         }
       });
     }
    }
    $('.filtreaxe').click(function() {
      var data = $(this).data();
      if (!filtres_axes[data.axe][data.item]) {
        var chip = '<div data-axe='+data.axe+' data-item='+data.item+' class="chip">'+axes.noms[data.axe]+':'+axes.defs[axes.noms[data.axe]].items[data.item][1]+'<i class="close closefilter material-icons">close</i></div>';
        $('#filtres').append(chip);
        $('.closefilter').click(function() {
          var data=$(this).parent().data();
          filtres_axes[data.axe][data.item] = false;
          $('input[data-axe="'+data.axe+'"][data-item="'+data.item+'"]').prop('checked',false);
          if (current_axe != data.axe) {
            selectAxe(current_axe);
          }
        });
      } else {

        $('.chip[data-axe="'+data.axe+'"][data-item="'+data.item+'"]').remove();
      }
      filtres_axes[data.axe][data.item] = !filtres_axes[data.axe][data.item];

    });


  }



$(document).ready( function() {

  $.ajax({
    //url: 'https://cdn.rawgit.com/maxkfranz/3d4d3c8eb808bd95bae7/raw', // wine-and-cheese.json
    url: 'json/axes.json',
    type: 'GET',
    dataType: 'json'
  }).done(function(data) {
    axes = data;

    for (i=0; i<axes.noms.length; i++) {
      $('#axes').append('<a class="axe waves-effect waves-light btn" n='+i+'>'+axes.noms[i]+'</a> ');
      filtres_axes[i]=[];
      for (j=0;j<axes.defs[axes.noms[i]].items.length;j++) {
        filtres_axes[i].push(false);
      }
    }
    $('.axe').click(function() {
      var axen = $(this).attr('n');
      selectAxe(axen);
    });

  });
});
