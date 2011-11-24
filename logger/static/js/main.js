LoggerApplication = function() {
  
  this.LogsState = Backbone.Model.extend({
    MAP_LEVELS: {
        'crit': 'critical',
        'debg': 'debug',
        'warn': 'warning',
        'info': 'info',
        'other': 'other'
    },
    
    MAP_SECTIONS: {}, // Will be initialized in constructor
      
    defaults: {
      show_critical: true,
	  show_warning:  true,
	  show_debug:    true,
	  show_info:     true,
      show_other:    true,
      count_critical: 0,
      count_warning:  0,
      count_debug:    0,
      count_info:     0,
      count_other:    0
    },
    initialize: function() {
        var that = this;
        _.each(this.MAP_LEVELS, function(v, k) {
            that.MAP_SECTIONS[k] = $('section#logs-' + v);
        });
    },
    get_states: function() {
        var result = {};
        var attributes = this.toJSON();
        _.each(attributes, function(v, k) {
           if (k.slice(0, 5) == 'show_') {
               result[k.slice(5, 20)] = v;
           }  
        });
        return result;
    },
    get_counts: function() {
        var result = {};
        var attributes = this.toJSON();
        _.each(attributes, function(v, k) {
           if (k.slice(0, 6) == 'count_') {
               result[k.slice(6, 20)] = v;
           }  
        });
        return result;            
    },
    get_section: function(lvl) {
        var section = this.MAP_SECTIONS[lvl];
        if (!section) {
            section = this.MAP_SECTIONS['other'];
        }
        return section;
    },
    // Returns updatable section, or null, if it's disabled
    handle_event: function(event) {
        var result = false;
        var level = this.MAP_LEVELS[event.level];
        if (this.get('show_'+level)) {
            result = true;
            var o = {};
            o['count_'+level] = this.get('count_'+level)+1;
            this.set(o);
        }
        return result;
    }
  });
  
  this.logsState = new this.LogsState();
  
  var PreferencesView = Backbone.View.extend({
	el: $("div#prefs"),
	
	events: {
		"click input:checkbox": "check"
	},
	
	initialize: function() {
		this.model.bind('change', this.render, this);
	},
	check: function(e) {
	    var el = $(e.target);
	    var obj = {}
	    obj[el.attr('id')] = Boolean(el.attr('checked'));
		this.model.set(obj);
	},
	render: function() {
	    _.each(this.model.get_states(), function(v, k) {
		    $("input#show_"+k, this.el).attr('checked', v);
	    });
	}
  });

  var TabsView = Backbone.View.extend({
    el: $('nav#tabs'),
    
    initialize: function() {
        this.model.bind('change', this.render, this);
    },
    render: function() {
        var that = this;
        _.each(this.model.get_counts(), function(v, k) {
            var el = $("a[href='#"+k+"']", this.el).next();
            if (that.model.get('show_'+k)) {
                el.html('['+v+']');
            } else {
                el.html('');
            }
        });
    } 
  });
	
	
  var preferences = new PreferencesView({ model: this.logsState });
  var tabs        = new TabsView({ model: this.logsState })

  var Controller = Backbone.Router.extend({
    routes: {
      ''         : 'index',
      ':type'    : 'logs'
    },
    render_template: $('#log_msg_template'),
    initialize: function(options) {
        this.logsState = options.logsState;
        this.logsState.change();
	},
    toggleNav: function(type) {
      $('nav#tabs li').removeClass('current');
      $('nav#tabs a[href="#'+type+'"]').parent().addClass('current');
    },
    hideAll: function() {
      $('div#log-output > section').removeClass('current');
    },
    index: function() {
      this.toggleNav('');
      this.hideAll();
      $('section#index').addClass('current');
    },
    logs: function(type) {
      this.toggleNav(type);
      this.hideAll();
      $('section#logs-' + type).addClass('current');
    },
    new_event: function(event) {
      if (this.logsState.handle_event(event)) {
          section = this.logsState.get_section(event.level);
          
          render_item = this.render_template.clone();
          render_item.removeClass('none').removeAttr('id');

          $('span.log_time', render_item).text(event.time)
          $('span.log_type', render_item).text(event.type)
          $('span.log_message', render_item).text(event.msg)

          section.prepend(render_item);
          while (section.children().length > 100) {
              section.children().last().remove();
          }
      }
    }
  });
  
  this.start = function() {
      var controller = new Controller({ logsState: this.logsState });
      Backbone.history.start();

      if (typeof window !== 'undefined'){
          window.WEB_SOCKET_SWF_LOCATION = '/static/js/vendor/WebSocketMain.swf';
      }
      var socket = io.connect('/');
  
      socket.on('log', function(event) {
          controller.new_event(event);
      });
  }
  
  return this;
}