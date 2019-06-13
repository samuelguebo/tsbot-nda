jQuery( document ).ready( function( $ ) {
    
    $('#contribs-form-wrapper form').submit(function(e) {
        e.preventDefault(); // disable default behavior
        contribsFormHandler(this);
    })

    /**
     * Handle data related to CU Audit form 
     * @link: https://developers.google.com/apps-script/guides/html/communication
     */
    function contribsFormHandler(formObject) {
        var rows = [];
        var username = $(formObject).find("input[name=username]").val();
        var wiki = $(formObject).find("input[name=wiki]").val();
        
        getWikiContribs(wiki, username)
            .then(function(contribs){
                
                for (var i = 0; i <= contribs.length; i++) {
                    
                    var edit = contribs[i];
                    var line = i+1
                    if (typeof(edit) !== "undefined"){

                        // Append row to Table
                        var html = '<tr>'
                        html += '<td>' + line + '</td>'
                        html += '<td>' + edit.timestamp + '</td>'
                        html += '<td>' + edit.revid + '</td>'
                        html += '<td>' + edit.user + '</td>'
                        html += '<td>' + edit.title + '</td>'
                        html += '<td>' + edit.comment + '</td>'
                        html += '</tr>'
                        
                        $('#contribs-table tbody:last-child')
                        .append(html);

                        console.log(edit)
                    }
                    
                    
                } 
                
                
            })
        
        
    }

    /**
     * Get user contributions via API:Contribs
     * @link: https://www.mediawiki.org/wiki/API:Usercontribs
     */
    function getWikiContribs(wiki, username) {
        var limit = 50;
        // Get the base url
        baseUrl = getBaseUrl();
        var query = "uclimit=" + limit +
        "&format=json&list=usercontribs&ucuser=" + username;
        url = baseUrl + "query/" + query + "/" + wiki
        console.log("url: " + url)    
        
        
        return fetch(url)
                .then(function(data){
                    return data.json()
                })
                .then(function(json){
                    return json.query.usercontribs
                })      
    }

    /**
     * Get Homeurl
     */
    function getBaseUrl() {
        // use home url link as baseurl, remove protocol
        var baseUrl = document.getElementById( 'baseurl' ).getAttribute( 'href' ).replace( /^https?:\/\//,'' );
        // add actual protocol to fix Flask bug with protocol inconsistency
        //baseUrl = location.protocol + '//' + baseUrl
        return baseUrl;
    }
} );

