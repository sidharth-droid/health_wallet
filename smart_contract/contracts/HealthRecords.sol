pragma solidity ^0.8.0;

contract HealthRecords {
    struct Record {
        string condition;
        string treatmentDetails;
        address owner;
        bool isActive;  
    }

    struct Permission {
        bool canView;
        bool canEdit;
        bool canDelete;
        bool isPermanent;
        uint256 expiryTime;
    }

    mapping(uint256 => Record) public records;
    mapping(uint256 => mapping(address => Permission)) public recordPermissions; // Permission mapping

    uint256 public recordCount;

    event RecordAdded(uint256 indexed recordId, string condition, string treatmentDetails, address indexed owner);
    event RecordUpdated(uint256 indexed recordId, string condition, string treatmentDetails);
    event AccessGranted(uint256 indexed recordId, address indexed provider, bool canView, bool canEdit, bool canDelete, bool isPermanent);
    event AccessRevoked(uint256 indexed recordId, address indexed provider);

    function addRecord(string memory condition, string memory treatmentDetails) public {
        recordCount++;
        records[recordCount] = Record(condition, treatmentDetails, msg.sender, true);
        emit RecordAdded(recordCount, condition, treatmentDetails, msg.sender);
    }

    function getRecord(uint256 recordId) public view returns (string memory, string memory, address) {
        Record memory record = records[recordId];
        return (record.condition, record.treatmentDetails, record.owner);
    }

    function deleteRecord(uint256 recordId) public {
        require(records[recordId].owner == msg.sender, "Not the owner");
        delete records[recordId];
    }

    function updateRecord(uint256 recordId, string memory condition, string memory treatmentDetails) public {
        require(records[recordId].owner == msg.sender, "Not the owner");
        records[recordId].condition = condition;
        records[recordId].treatmentDetails = treatmentDetails;
        emit RecordUpdated(recordId, condition, treatmentDetails);
    }

    function toggleRecordActive(uint256 recordId, bool isActive) public {
        require(records[recordId].owner == msg.sender, "Not the owner");
        records[recordId].isActive = isActive;
    }

    function grantAccess(
        uint256 recordId,
        address provider,
        bool canView,
        bool canEdit,
        bool canDelete,
        bool isPermanent,
        uint256 expiryTime
    ) public {
        require(records[recordId].owner == msg.sender, "Not the owner");
        recordPermissions[recordId][provider] = Permission(canView, canEdit, canDelete, isPermanent, expiryTime);
        emit AccessGranted(recordId, provider, canView, canEdit, canDelete, isPermanent);
    }

    function revokeAccess(uint256 recordId, address provider) public {
        require(records[recordId].owner == msg.sender, "Not the owner");
        delete recordPermissions[recordId][provider];
        emit AccessRevoked(recordId, provider);
    }

    function canAccess(uint256 recordId, address provider) public view returns (bool) {
        Permission memory permission = recordPermissions[recordId][provider];
        return permission.canView && (permission.isPermanent || permission.expiryTime > block.timestamp);
    }

    // New function to retrieve access permissions for a specific provider
    function getAccessPermissions(uint256 recordId, address provider) 
        public 
        view 
        returns (bool canView, bool canEdit, bool canDelete, bool isPermanent, uint256 expiryTime) 
    {
        Permission memory permission = recordPermissions[recordId][provider];
        return (permission.canView, permission.canEdit, permission.canDelete, permission.isPermanent, permission.expiryTime);
    }
}
