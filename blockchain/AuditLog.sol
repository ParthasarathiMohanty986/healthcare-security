// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AuditLog {
    
    // Event for logging actions
    event LogCreated(
        uint256 indexed logId,
        address indexed user,
        string action,
        string resourceType,
        string resourceId,
        bool accessGranted,
        bool isEmergency,
        uint256 timestamp,
        string ipAddress
    );

    // Event for log query
    event LogRetrieved(
        uint256 indexed logId,
        address indexed user,
        uint256 timestamp
    );

    // Structure to store audit logs
    struct AuditLogEntry {
        uint256 logId;
        address user;
        string action;
        string resourceType;
        string resourceId;
        bool accessGranted;
        bool isEmergency;
        string details;
        uint256 timestamp;
        string ipAddress;
    }

    // Contract owner (Django backend)
    address public owner;
    
    // Counter for log IDs
    uint256 public logCounter;
    
    // Mapping to store logs
    mapping(uint256 => AuditLogEntry) public logs;
    
    // Array to track all log IDs
    uint256[] public logIds;
    
    // Mapping to track logs by user
    mapping(address => uint256[]) public userLogs;

    // Access control mapping
    mapping(address => bool) public authorizedWriters;

    // Constructor
    constructor() {
        owner = msg.sender;
        logCounter = 0;
        authorizedWriters[msg.sender] = true;
    }

    // Modifier to restrict functions
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedWriters[msg.sender], "Not authorized to write logs");
        _;
    }

    // Function to authorize a writer (Django backend address)
    function authorizeWriter(address _address) public onlyOwner {
        authorizedWriters[_address] = true;
    }

    // Function to revoke writer authorization
    function revokeWriter(address _address) public onlyOwner {
        authorizedWriters[_address] = false;
    }

    // Function to create a new audit log entry
    function createAuditLog(
        address _user,
        string memory _action,
        string memory _resourceType,
        string memory _resourceId,
        bool _accessGranted,
        bool _isEmergency,
        string memory _details,
        string memory _ipAddress
    ) public onlyAuthorized returns (uint256) {
        
        uint256 newLogId = logCounter;
        logCounter++;

        // Create new log entry
        AuditLogEntry memory newLog = AuditLogEntry({
            logId: newLogId,
            user: _user,
            action: _action,
            resourceType: _resourceType,
            resourceId: _resourceId,
            accessGranted: _accessGranted,
            isEmergency: _isEmergency,
            details: _details,
            timestamp: block.timestamp,
            ipAddress: _ipAddress
        });

        // Store the log
        logs[newLogId] = newLog;
        logIds.push(newLogId);
        userLogs[_user].push(newLogId);

        // Emit event
        emit LogCreated(
            newLogId,
            _user,
            _action,
            _resourceType,
            _resourceId,
            _accessGranted,
            _isEmergency,
            block.timestamp,
            _ipAddress
        );

        return newLogId;
    }

    // Function to retrieve a specific log
    function getAuditLog(uint256 _logId) public returns (AuditLogEntry memory) {
        require(_logId < logCounter, "Log ID does not exist");
        
        emit LogRetrieved(_logId, msg.sender, block.timestamp);
        return logs[_logId];
    }

    // Function to get all logs (paginated)
    function getAllLogs(uint256 _startIndex, uint256 _limit) public view returns (AuditLogEntry[] memory) {
        require(_startIndex < logCounter, "Start index out of bounds");
        
        uint256 endIndex = _startIndex + _limit > logCounter ? logCounter : _startIndex + _limit;
        uint256 resultSize = endIndex - _startIndex;
        
        AuditLogEntry[] memory result = new AuditLogEntry[](resultSize);
        
        for (uint256 i = 0; i < resultSize; i++) {
            result[i] = logs[logIds[_startIndex + i]];
        }
        
        return result;
    }

    // Function to get logs for a specific user
    function getUserLogs(address _user, uint256 _startIndex, uint256 _limit) public view returns (AuditLogEntry[] memory) {
        uint256[] memory userLogIds = userLogs[_user];
        require(_startIndex < userLogIds.length, "Start index out of bounds");
        
        uint256 endIndex = _startIndex + _limit > userLogIds.length ? userLogIds.length : _startIndex + _limit;
        uint256 resultSize = endIndex - _startIndex;
        
        AuditLogEntry[] memory result = new AuditLogEntry[](resultSize);
        
        for (uint256 i = 0; i < resultSize; i++) {
            result[i] = logs[userLogIds[_startIndex + i]];
        }
        
        return result;
    }

    // Function to get total number of logs
    function getTotalLogs() public view returns (uint256) {
        return logCounter;
    }

    // Function to get number of logs for a user
    function getUserLogCount(address _user) public view returns (uint256) {
        return userLogs[_user].length;
    }

    // Function to verify immutability (read a log by ID)
    function verifyLog(uint256 _logId) public view returns (bool) {
        require(_logId < logCounter, "Log ID does not exist");
        return true;
    }
}
