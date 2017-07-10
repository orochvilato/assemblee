var db = new loki('sandbox.db');
// Add a collection to the database
var votants = db.addCollection('votants');
var axes;
var scrutins = [];
var filtres_axes=[];
var current_axe = 0;
var current_elements = [];
var exprimes = true;

function sort_particip(a,b) {
  return (a.participation - b.participation);
 };
 function sort_alpha(a,b) {
    return a.titre>b.titre;
 };
 function sort_pour(a,b) {
    return (a.elem_stats.pour/a.item_stats.n) - (b.elem_stats.pour/b.item_stats.n);
 };
 function sort_contre(a,b) {
    return (a.elem_stats.contre/a.item_stats.n) - (b.elem_stats.contre/b.item_stats.n);
 };
 function sort_abstention(a,b) {
    return (a.elem_stats.abstention/a.item_stats.n) - (b.elem_stats.abstention/b.item_stats.n);
 };




var sort_fcts = [  ['% participation',sort_particip],
              ['% vote pour',sort_pour],
              ['% vote contre',sort_contre],
              ['% vote abstention',sort_abstention],
              ['% ordre alphabétique',sort_alpha] ]
var current_sort = 0;
var current_sort_asc = false;

var loadVotants = function (data) {
  scrutins.push(data)
  data['positions'].forEach(function (p) {
     votants.insert(p);
  });
};
var loadScrutin= function(s) {
  votants.clear();
  scrutins = [];
  var calls = [];
  $('#scrutin option').each(function(){
    if (((s == 'tous') && ($(this).val() != 'tous')) || (($(this).val() == s) && ( s != 'tous')))
    {
        calls.push($.ajax({
          url: 'json/scrutin'+$(this).val()+'.json?t='+Date.now(),
          type: 'GET',
          dataType: 'json',
          success: loadVotants
        }));
    }
  });
  console.log(calls);
  $.when.apply(this, calls).done(function() {
    if (calls.length==1) {
      $('#titrescrutin').html('Scrutin n°'+scrutins[0].numero+' : '+scrutins[0].libelle);
    } else {
      $('#titrescrutin').html(scrutins.length+' scrutins');
    }

    selectAxe(current_axe);

  })


}

var sortElements = function() {

    current_elements.sort(sort_fcts[current_sort][1]);
    if (!current_sort_asc) {
      current_elements.reverse();
    }
    current_charts = [];

    $('#vue').empty().hide();
    var template = document.getElementById('template').innerHTML;
    Mustache.parse(template);

    for (var i=0;i<current_elements.length;i++) {
      var element = current_elements[i];
      var def = axes.defs[axes.noms[element.axe]];
      var rendered = Mustache.render(template, element);

      $('#vue').append(rendered);

      if (!def.hidechart) {
        var ctx = document.getElementById("donut"+element.i);
        var randomScalingFactor = function() {
         return Math.round(Math.random() * 100);
        };
        var data = []
        for (var j=0;j<element['stats'].length;j++) {
          data.push(element['stats'][j].n);
        }
        var myChart = new Chart(ctx, {
         type: 'doughnut',
         data: {
             datasets: [{
                 data: data,
                 backgroundColor: [
                     "green",
                     "red",
                     "dodgerblue",
                     "grey",
                     "grey",
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
             },
             tooltips: {
                  callbacks: {
                    label: function(tooltipItem, data) {
                      var allData = data.datasets[tooltipItem.datasetIndex].data;
                      var tooltipLabel = data.labels[tooltipItem.index];
                      var tooltipData = allData[tooltipItem.index];
                      var total = 0;
                      for (var i in allData) {
                        total += allData[i];
                      }
                      var tooltipPercentage = Math.round((tooltipData / total) * 100);
                      return tooltipLabel + ': ' + tooltipData + ' (' + tooltipPercentage + '%)';
                    }
                  }
              }
         }
       });
     }
    }

    $('.filtreaxe').click(function() {
      var data = $(this).data();
      if (!filtres_axes[data.axe][data.item]) {
        var chip = '<div data-axe='+data.axe+' data-item='+data.item+' class="chip teal">'+axes.noms[data.axe]+':'+axes.defs[axes.noms[data.axe]].items[data.item][1]+'<i class="close closefilter material-icons">close</i></div>';
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
    $('#vue').show();
}
var selectAxe = function(axen) {
    var def = axes.defs[axes.noms[axen]];
    current_axe = axen;
    $('#titreaxe').html(def.titre);
    var elements = [];

    for (var i=0; i<def.items.length; i++) {
      //$('#vue').append('<h4>'+def.items[i][1]+'</h4>');
      var sel = {};
      var cmp = {}
      cmp[def.compare] = def.items[i][0];
      sel[def.field] = cmp
      var req = { '$and':[]};

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
      var base = votants.find(req).length;
      req['$and'].push(sel)
      var results = votants.find(req);
      if (results.length>0) {
        var stats = { pour:0, contre:0, abstention:0, 'nonVotant':0, absent:0};
        for (var j=0; j<results.length;j++) {
          stats[results[j].position] += 1;
        }
        var stats_exprimes =[];
        var stats_general=[];
        var positions =  ['pour','contre','abstention','nonVotant','absent'];
        var positionsVotants = ['pour','contre','abstention'];
        var icons = { pour:'thumbs-up', contre:'thumbs-down', abstention:'meh-o', 'nonVotant':'ban', 'absent':'plane'};
        var libelles = { pour:'votes pour', contre:'votes contre', abstention:'abstention', 'nonVotant':'non votants (justifiés)', 'absent':'absents'};
        var item_stats =  { n: results.length/scrutins.length, pct: Math.round(100*(results.length/base))};
        var nvotants = results.length - stats['absent'] - stats['nonVotant']
        var maxexprime = Math.max(stats['pour'],stats['contre'],stats['abstention']);
        var maxgeneral = Math.max(stats['pour'],stats['contre'],stats['abstention'],stats['nonVotant'],stats['absent']);
        positionsVotants.forEach(function(p) {
          stats_exprimes.push({ nul: (stats[p]==0), libelle:libelles[p], big: (stats[p]==maxexprime), position:p, n:stats[p], pct:Math.round(100*stats[p]/nvotants), icon:icons[p] });
        });
        positions.forEach(function(p) {
          stats_general.push({ nul: (stats[p]==0), libelle:libelles[p], big: (stats[p]==maxgeneral), position:p, n:stats[p], pct:Math.round(100*stats[p]/results.length), icon:icons[p] });
        });


        var _cercles =  { pour:[], contre:[], abstention:[], 'nonVotant':[], absent:[] };
        results.forEach(function(r) {
          _cercles[r.position].push(r);
        });
        var cercles = [];
        positions.forEach(function(p) {
          cercles = cercles.concat(_cercles[p]);
        })

        elements.push({
                       monoscrutin:(scrutins.length==1),
                       filtered:filtres_axes[axen][i],
                       i:i,
                       assemblee:(axen==0),
                       axe:axen,hidechart:def.hidechart,
                       key: def.items[i][0],
                       titre: def.items[i][1],
                       cercles: cercles,
                       exprimes: exprimes,
                       participation : Math.round(100*nvotants/(results.length-stats['nonVotant'])),
                       stats:(exprimes ? stats_exprimes : stats_general),
                       item_stats:item_stats,
                       elem_stats:stats});
      }
    }
    current_elements = elements;
    sortElements();
  }



$(document).ready( function() {
  for (var i=0;i<sort_fcts.length;i++) {
    var s = sort_fcts[i];
    var badge = ( current_sort == i ? 'new':'')
    var sens = ( current_sort_asc ? ' asc ' : ' desc ')

    $('#tris').append('<span data-i="'+i+'" class="'+badge+sens+'badge tri" data-badge-caption="'+s[0]+'"><i class="fa fa-sort-asc asc"></i><i class="fa fa-sort-desc desc"></i></span>');
  }
  $('.tri').click(function () {
    if ($(this).hasClass('new')) {
      $(this).removeClass('asc desc');
      current_sort_asc = !current_sort_asc

    } else {
      $('.tri').removeClass('new').removeClass('asc desc');
      $(this).addClass('new');
      current_sort = $(this).data().i;
    }
    var sens = ( current_sort_asc ? ' asc ' : ' desc ');
    $(this).addClass(sens);
    sortElements();
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
      filtres_axes[i]=[];
      for (j=0;j<axes.defs[axes.noms[i]].items.length;j++) {
        filtres_axes[i].push(false);
      }
    }
    $('.axe').click(function() {
      var axen = $(this).attr('n');
      selectAxe(axen);
    });
    $('#suffrages').click(function () {
      exprimes = !exprimes;
      libelle = (exprimes ? 'Suffrages exprimés':'Tous les députés')
      $(this).attr('data-badge-caption',libelle);
      selectAxe(current_axe);
    });
  });
});
