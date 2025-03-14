// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract poultry {

  string[] _cretailers;
  address[] _consumers;
  string[] _cnames;
  string[] _clocations;
  string[] _ckgs;
  string[] _cproducttypes;
  uint[] _corderids;
  uint[] _cstatuses;
  string[] _consumeremails;

  address[] _oretailers;
  string[] _onames;
  string[] _olcations;
  string[] _okgs;
  string[] _oproducttypes;
  uint[] _oorderids;
  uint[] _ostatuses;
  string[] _oemails;


  uint orderid;
  uint oorderid;

  constructor() {
    orderid=0;
    oorderid=0;
  }

  function addConsumer(string memory cemail,string memory cretailer,address consumer,string memory cname,string memory clocation,string memory ckg,string memory cproducttype) public {
    orderid+=1;
    _consumeremails.push(cemail);
    _cretailers.push(cretailer);
    _corderids.push(orderid);
    _consumers.push(consumer);
    _cnames.push(cname);
    _clocations.push(clocation);
    _ckgs.push(ckg);
    _cproducttypes.push(cproducttype);
    _cstatuses.push(0);
  }

  function viewConsumers() public view returns (string[] memory,string[] memory,uint[] memory,uint[] memory,address[] memory,string[] memory,string[] memory,string[] memory,string[] memory){
    return(_consumeremails,_cretailers,_cstatuses,_corderids,_consumers,_cnames,_clocations,_ckgs,_cproducttypes);
  }

  function updateOrder1(uint cid,uint cstatus) public {
    uint i;

    for(i=0;i<_corderids.length;i++){
      if(_corderids[i]==cid){
        _cstatuses[i]=cstatus;
      }
    }
  }

  function addOrder(string memory oemail,address retailer,string memory rname,string memory rlocation,string memory rkgs,string memory rtype) public {
    oorderid+=1;
    _oemails.push(oemail);
    _oorderids.push(oorderid);
    _okgs.push(rkgs);
    _olcations.push(rlocation);
    _onames.push(rname);
    _oretailers.push(retailer);
    _oproducttypes.push(rtype);
    _ostatuses.push(0);
  }

  function viewOrders() public view returns(string[] memory,uint[] memory,address[] memory,uint[] memory,string[] memory,string[] memory,string[] memory,string[] memory) {
    return(_oemails,_oorderids,_oretailers,_ostatuses,_onames,_olcations,_oproducttypes,_okgs);
  }

  function updateOrder(uint oid,uint status) public {
    uint i;

    for(i=0;i<_oorderids.length;i++){
      if(_oorderids[i]==oid){
        _ostatuses[i]=status;
      }
    }
  }
}
