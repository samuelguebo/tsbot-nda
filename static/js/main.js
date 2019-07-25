

jQuery( document ).ready( function( $ ) {

    /* Form variables */
    var contribs_form = $('#contribs-form-wrapper form')
    var contribs_table = $('#contribs-form-wrapper #contribs-table')
    var contribs_notification = $('#contribs-form-wrapper #notification')
    var contribs_collection = []


    /* Search through MediaWiki API */
    $('#contribs-form-wrapper #btn-search').click(function(e){
        e.preventDefault();
        var operation = contribs_form.find("select[name=operation]")
        if (typeof(operation) !== "undefined") {
          revertsHandler(contribs_form);
        }else{
          contribsHandler(contribs_form);
        }

    })

    /* Save rows to db */
    $('#contribs-form-wrapper #btn-save').click(function(e){
        e.preventDefault();
        saveContribs(contribs_collection)
        .then(function(response){
            return response.json()
        }).then(function(json){
            var result_id = json.result_id
            var result_url = new Utils().getBaseUrl() + "contribs/view/" + result_id
            var html = "The search was saved with link "
                html += "<a href='"
                html += result_url + "'>"
                html += result_url
                html += "</a>"

            $('#contribs-form-wrapper #btn-save').remove()
            $('#contribs-form-wrapper #btn-search').remove()

            contribs_notification.html(html)
            return
        }).catch(function(error){
            var html = "An error occurred, the search was not saved."
            contribs_notification.html(html)
            return
        })
    })

    /* Clear the table rows */
    $('#contribs-form-wrapper #btn-reset').click(function(e){
        e.preventDefault();
        contribs_table.find('tbody').empty()
    })


    /**
     * Handle data related to Contribs search operation
     * @link: https://developers.google.com/apps-script/guides/html/communication
     */
    function contribsHandler(formObject) {

        var username = $(formObject).find("input[name=username]").val();
        var wiki = $(formObject).find("input[name=wiki]").val();

        if(""!== wiki && ""!= username){
            var mediawiki = new MediaWiki(wiki, username)
            mediawiki
            .getWikiContribs()
                .then(function(contribs){
                  fillHTMLTable(wiki, contribs)
                })
        }

    }

    /**
     * Handle data related to CU Audit form
     * @link: https://developers.google.com/apps-script/guides/html/communication
     */
    function revertsHandler(formObject) {
        var username = $(formObject).find("input[name=username]").val();
        var wiki = $(formObject).find("input[name=wiki]").val();

        if(""!== wiki && ""!= username){
            var mediawiki = new MediaWiki(wiki, username)
            mediawiki
            .getWikiContribs()
              .then(function(contribs){
                  var promises = []
                  var filteredEdits = []
                  for (var i = 0; i < contribs.length; i++){
                      var edit = contribs[i]
                      filterPromise = new Promise(function(resolve, reject){
                        mediawiki.isEditReverted(edit)
                        .then(function(response){
                          if (response){
                            filteredEdits.push(edit)
                          }
                        })
                      })
                      promises.push(filterPromise)
                  }

                return Promise.all(promises)
                 .then(function(){
                   return filteredEdits;
                 })
                .then(function(filteredEdits) {
                  fillHTMLTable(wiki, filteredEdits)
                })
            })

    }
  }

    /**
     * Utility: Fill the HTML tabled
     * @type {Utils}
     */
     function fillHTMLTable(wiki, contribs){

         for (var i = 0; i <= contribs.length; i++) {

             // Add edit to the collection of contribs
             var edit = contribs[i];

             if (typeof(edit) !== "undefined"){
                 contribs_collection.push(edit)
                 var line = contribs_collection.length
                 // Append row to Table
                 var html = '<tr>'
                         html += '<td>' + line + '</td>'
                         html += '<td>' + edit.timestamp + '</td>'
                         html += '<td><a href="https://' + wiki
                                    + '/wiki/Special:Diff/' + edit.revid + '">'
                                    + edit.revid + '</a></td>'
                         html += '<td>' + edit.user + '</td>'
                         html += '<td>' + edit.title + '</td>'
                         html += '<td>' + edit.comment + '</td>'
                     html += '</tr>'

                 $('#contribs-table tbody:last-child')
                 .append(html);


             }

         }

     }
     /**
      * Post result to endpoint. Once its hits the route
      * It will be saved in the DB
      * */
     function saveContribs(contribs){

         var url = new Utils().getBaseUrl() + "contribs/save"
         return fetch(url, {
                     method: 'PUT',
                     body: JSON.stringify(contribs),
                     headers: {
                         'Content-Type': 'application/json'
                     }
                 })
                 .then(function(response){
                     return response
                 })
     }


     /**
      * Performs a various range of interactions with
      * the MediaWiki REST API
      * @link: https://www.mediawiki.org/wiki/API:Help
      */
     class MediaWiki {
         /**
          * Constructor
          * @param {String} wiki
          * @param {String} username
          */
         constructor(wiki, username){
             this.wiki = wiki;
             this.username = username;
         }

         /**
          * Get user contributions via API:Contribs
          * @link: https://www.mediawiki.org/wiki/API:Usercontribs
          */
         getWikiContribs() {
             var limit = 50;
             // Get the base url
             var baseUrl = new Utils().getBaseUrl();
             var query = "uclimit=" + limit
             // Add support for tags
             query += "&ucprop=tags|flags|title|comment&list=usercontribs"
             query += "&ucuser=" + this.username";
             query += "&format=json&list=usercontribs&ucuser=" + this.username;
             var url = baseUrl + "query/" + query + "/" + this.wiki

             return fetch(url)
                     .then(function(data){
                         return data.json()
                     })
                     .then(function(json){
                         return json.query.usercontribs
                     })
         }
         /**
          * Get user reverted edits via API:Contribs and
          * @link: https://www.mediawiki.org/wiki/API:Usercontribs
          */
         isEditReverted(edit) {
           // Check wether revision has item "suppressed"
           return "undefined" !== edit.suppressed;
         }

         /**
          * Get next revision
          * @link: https://www.mediawiki.org/wiki/API:Compare
          */
         getNextRevision(edit){
           // Get the base url
           var baseUrl = new Utils().getBaseUrl();
           var query = "action=compare&fromrev=" + edit.revid
           query += "&prop=comment|user|title&torelative=next&format=json"
           //query = query.replace("|", "%7C")
           var url = baseUrl + "query/" + query + "/" + this.wiki

           return fetch(url)
                   .then(function(data){
                       return data.json()
                   })
                   .then(function(json){
                     var result = json.compare
                        console.log(result)
                       return result

                   })

         }

     }

     class Utils {
         /**
          * Get Homeurl
          */
         getBaseUrl() {
             // use home url link as baseurl, remove protocol
             var baseUrl = document.getElementById( 'baseurl' ).getAttribute( 'href' ).replace( /^https?:\/\//,'' );
             // add actual protocol to fix Flask bug with protocol inconsistency
             // baseUrl = location.protocol + '//' + baseUrl
             return baseUrl;
         }
     }
 });
