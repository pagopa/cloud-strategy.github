locals {
  identitystore_group_import_ids = {
    "platform" = "d-1/g-1"
  }
}

import {
  for_each = local.identitystore_group_import_ids
  to       = aws_identitystore_group.groups[each.key]
  id       = each.value
  provider = aws.identity_center
}
