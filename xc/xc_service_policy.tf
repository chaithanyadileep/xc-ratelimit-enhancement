resource "volterra_service_policy" "allow_all" {
    name        = "allow-all-test-ideathon"
    namespace   = "kvm-on-prem"
    algo        = "FIRST_MATCH"
    any_server  = true


    rule_list {
    rules {
      metadata {
        name = "demo-rule"
      }
      spec {
        action     = "DENY"
        any_client = true
        waf_action {
          none = true
        }
        ip_prefix_list {
        ip_prefixes = [var.IP_list]
      }
      }
      
    }
    rules {
      metadata {
        name = "demo-rule-2"
      }
      spec {
        action     = "ALLOW"
        any_client = true
        waf_action {
          none = true
        }
      }
    }
  }

}














